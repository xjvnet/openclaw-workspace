#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股市场趋势分析工具
获取近一年市场数据，进行LLM分析，生成图表
"""

import os
import json
import datetime
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非交互式后端

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# Token
TOKEN = "4f3f83948659c9e3b20411b2cadaed9950b8146e4f367a38f45d6e02"
pro = ts.pro_api(TOKEN)

def get_stock_data():
    """获取A股股票基础数据"""
    print("[1/5] 获取股票基础数据...")
    df = pro.stock_basic(
        ts_code='',
        exchange='',
        list_status='L',
        fields='ts_code,symbol,name,area,industry,list_date,market,exchange'
    )
    print(f"  股票总数: {len(df)}")
    return df

def get_industry_data():
    """获取行业板块数据"""
    print("[2/5] 获取行业板块数据...")
    
    # 获取同花顺行业分类
    try:
        df = pro.ths_index(member_status='L')
        # 获取行业成分
        industries = df[['index_code', 'industry_name']].drop_duplicates()
        print(f"  行业板块数: {len(industries)}")
    except:
        # 备用：使用 stock_basic 的 industry 字段
        stocks = pro.stock_basic(fields='industry')
        industries = stocks['industry'].value_counts().reset_index()
        industries.columns = ['industry_name', 'count']
        print(f"  行业数: {len(industries)}")
    
    return industries

def get_index_data():
    """获取主要指数数据"""
    print("[3/5] 获取指数行情数据...")
    
    indices = {
        '000001.SH': '上证指数',
        '399001.SZ': '深证成指',
        '399006.SZ': '创业板指',
        '000300.SH': '沪深300',
        '000905.SH': '中证500'
    }
    
    # 一年前日期
    end_date = datetime.datetime.now().strftime('%Y%m%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y%m%d')
    
    index_data = {}
    for code, name in indices.items():
        try:
            df = pro.index_daily(ts_code=code, start_date=start_date, end_date=end_date)
            df = df.sort_values('trade_date')
            index_data[name] = df
            print(f"  {name}: {len(df)} 条数据")
        except Exception as e:
            print(f"  {name}: 获取失败 - {e}")
    
    return index_data

def analyze_trends(index_data, stock_data):
    """分析市场趋势"""
    print("[4/5] 分析市场趋势...")
    
    analysis = {
        '概览': {},
        '行业分布': {},
        '趋势特征': {}
    }
    
    # 计算各指数涨跌幅
    for name, df in index_data.items():
        if len(df) > 0:
            first_price = df.iloc[0]['close']
            last_price = df.iloc[-1]['close']
            change_pct = (last_price - first_price) / first_price * 100
            
            # 计算波动率
            df['returns'] = df['close'].pct_change()
            volatility = df['returns'].std() * np.sqrt(252) * 100
            
            # 近期趋势（最近20天）
            recent = df.tail(20)
            trend = '上涨' if recent['close'].iloc[-1] > recent['close'].iloc[0] else '下跌'
            
            analysis['概览'][name] = {
                '年涨跌幅': f"{change_pct:.2f}%",
                '波动率': f"{volatility:.2f}%",
                '近期趋势': trend,
                '最新收盘': f"{last_price:.2f}"
            }
    
    # 行业分布
    if 'industry' in stock_data.columns:
        top_industries = stock_data['industry'].value_counts().head(15)
        analysis['行业分布'] = {k: int(v) for k, v in top_industries.items()}
    
    # 趋势特征
    if '上证指数' in index_data and len(index_data['上证指数']) > 0:
        df = index_data['上证指数']
        
        # 计算均线
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma60'] = df['close'].rolling(60).mean()
        df['ma120'] = df['close'].rolling(120).mean()
        
        latest = df.iloc[-1]
        
        # 判断市场状态
        if latest['close'] > latest['ma20'] > latest['ma60']:
            status = "强势上涨"
        elif latest['close'] < latest['ma20'] < latest['ma60']:
            status = "弱势下跌"
        elif latest['ma20'] > latest['ma60']:
            status = "震荡上行"
        else:
            status = "震荡下行"
        
        analysis['趋势特征']['市场状态'] = status
        analysis['趋势特征']['20日均线'] = f"{latest['ma20']:.2f}"
        analysis['趋势特征']['60日均线'] = f"{latest['ma60']:.2f}"
    
    return analysis

def generate_charts(index_data, stock_data, analysis, output_dir):
    """生成图表"""
    print("[5/5] 生成图表...")
    
    charts = []
    
    # 1. 主要指数走势对比图
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # 归一化处理
    for name, df in index_data.items():
        if len(df) > 0:
            normalized = df['close'] / df['close'].iloc[0] * 100
            ax.plot(pd.to_datetime(df['trade_date']), normalized, label=name, linewidth=1.5)
    
    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    ax.set_title('Main Index Performance (Base=100)', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Relative Value')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    chart_path1 = os.path.join(output_dir, 'index_comparison.png')
    plt.savefig(chart_path1, dpi=150)
    charts.append(chart_path1)
    plt.close()
    print(f"  已生成: {chart_path1}")
    
    # 2. 行业分布饼图
    if 'industry' in stock_data.columns:
        fig, ax = plt.subplots(figsize=(12, 10))
        top_industries = stock_data['industry'].value_counts().head(15)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(top_industries)))
        wedges, texts, autotexts = ax.pie(
            top_industries.values,
            labels=top_industries.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        ax.set_title('Industry Distribution (Top 15)', fontsize=14)
        plt.tight_layout()
        
        chart_path2 = os.path.join(output_dir, 'industry_distribution.png')
        plt.savefig(chart_path2, dpi=150)
        charts.append(chart_path2)
        plt.close()
        print(f"  已生成: {chart_path2}")
    
    # 3. 上证指数技术分析图
    if '上证指数' in index_data and len(index_data['上证指数']) > 0:
        fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})
        
        df = index_data['上证指数'].copy()
        df = df.sort_values('trade_date')
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        
        # 价格和均线
        axes[0].plot(df['trade_date'], df['close'], label='Close', linewidth=1.5)
        axes[0].plot(df['trade_date'], df['close'].rolling(20).mean(), label='MA20', linewidth=1, alpha=0.8)
        axes[0].plot(df['trade_date'], df['close'].rolling(60).mean(), label='MA60', linewidth=1, alpha=0.8)
        axes[0].set_title('Shanghai Composite Index - Technical Analysis', fontsize=14)
        axes[0].set_ylabel('Price')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 成交量
        axes[1].bar(df['trade_date'], df['vol'], alpha=0.6, color='blue')
        axes[1].set_title('Volume', fontsize=12)
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('Volume')
        
        plt.tight_layout()
        
        chart_path3 = os.path.join(output_dir, 'shanghai_technical.png')
        plt.savefig(chart_path3, dpi=150)
        charts.append(chart_path3)
        plt.close()
        print(f"  已生成: {chart_path3}")
    
    # 4. 市场状态仪表盘
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 4.1 年涨跌幅
    if analysis.get('概览'):
        index_names = list(analysis['概览'].keys())
        changes = []
        for name in index_names:
            try:
                change = float(analysis['概览'][name]['年涨跌幅'].replace('%', ''))
                changes.append(change)
            except:
                changes.append(0)
        
        colors = ['green' if c > 0 else 'red' for c in changes]
        axes[0, 0].barh(index_names, changes, color=colors, alpha=0.7)
        axes[0, 0].axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        axes[0, 0].set_title('YTD Change %', fontsize=12)
        axes[0, 0].set_xlabel('Change %')
    
    # 4.2 波动率
    if analysis.get('概览'):
        volatilities = []
        for name in index_names:
            try:
                vol = float(analysis['概览'][name]['波动率'].replace('%', ''))
                volatilities.append(vol)
            except:
                volatilities.append(0)
        
        axes[0, 1].barh(index_names, volatilities, color='orange', alpha=0.7)
        axes[0, 1].set_title('Volatility (Annualized)', fontsize=12)
        axes[0, 1].set_xlabel('Volatility %')
    
    # 4.3 市场状态
    status = analysis.get('趋势特征', {}).get('市场状态', 'N/A')
    axes[1, 0].text(0.5, 0.5, status, ha='center', va='center', fontsize=24, 
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    axes[1, 0].set_title('Market Status', fontsize=12)
    axes[1, 0].axis('off')
    
    # 4.4 统计信息
    stats_text = f"Total Stocks: {len(stock_data)}\n"
    stats_text += f"Industries: {len(stock_data['industry'].unique())}\n"
    stats_text += f"Shanghai: {analysis.get('趋势特征', {}).get('20日均线', 'N/A')}\n"
    stats_text += f"60日均线: {analysis.get('趋势特征', {}).get('60日均线', 'N/A')}"
    
    axes[1, 1].text(0.1, 0.5, stats_text, ha='left', va='center', fontsize=14,
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    axes[1, 1].set_title('Statistics', fontsize=12)
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    
    chart_path4 = os.path.join(output_dir, 'market_dashboard.png')
    plt.savefig(chart_path4, dpi=150)
    charts.append(chart_path4)
    plt.close()
    print(f"  已生成: {chart_path4}")
    
    return charts

def generate_analysis_report(analysis, stock_data):
    """生成分析报告文本（供LLM分析用）"""
    
    report = f"""
## A股市场分析报告

### 一、市场概览

"""
    
    for name, data in analysis.get('概览', {}).items():
        report += f"**{name}**:\n"
        report += f"- 年涨跌幅: {data.get('年涨跌幅', 'N/A')}\n"
        report += f"- 波动率: {data.get('波动率', 'N/A')}\n"
        report += f"- 近期趋势: {data.get('近期趋势', 'N/A')}\n"
        report += f"- 最新收盘: {data.get('最新收盘', 'N/A')}\n\n"
    
    report += f"""
### 二、行业分布

股票总数: {len(stock_data)}
行业数: {len(stock_data['industry'].unique())}

前十大行业:
"""
    
    top_ind = stock_data['industry'].value_counts().head(10)
    for ind, cnt in top_ind.items():
        report += f"- {ind}: {cnt} 只\n"
    
    report += f"""
### 三、趋势特征

- 市场状态: {analysis.get('趋势特征', {}).get('市场状态', 'N/A')}
- 20日均线: {analysis.get('趋势特征', {}).get('20日均线', 'N/A')}
- 60日均线: {analysis.get('趋势特征', {}).get('60日均线', 'N/A')}

### 四、分析建议

请基于以上数据，分析：
1. 当前市场处于什么阶段？
2. 哪些行业具有投资机会？
3. 板块轮动规律是什么？
4. 风险提示和建议？
"""
    
    return report

def main():
    """主函数"""
    print("=" * 50)
    print("A股市场趋势分析工具")
    print("=" * 50)
    
    # 创建输出目录
    output_dir = os.path.expanduser("~/.openclaw/workspace/skills/market-analysis/output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取数据
    stock_data = get_stock_data()
    industry_data = get_industry_data()
    index_data = get_index_data()
    
    # 分析
    analysis = analyze_trends(index_data, stock_data)
    
    # 生成图表
    charts = generate_charts(index_data, stock_data, analysis, output_dir)
    
    # 生成报告
    report = generate_analysis_report(analysis, stock_data)
    report_path = os.path.join(output_dir, 'analysis_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存: {report_path}")
    
    # 保存分析数据
    data_path = os.path.join(output_dir, 'analysis_data.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"数据已保存: {data_path}")
    
    print("\n" + "=" * 50)
    print("分析完成！")
    print(f"图表位置: {output_dir}")
    print("=" * 50)
    
    return {
        'charts': charts,
        'report': report_path,
        'data': data_path,
        'analysis': analysis
    }

if __name__ == "__main__":
    main()