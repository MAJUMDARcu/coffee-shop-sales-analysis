import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'figure.facecolor': '#FAFAFA',
    'axes.facecolor': '#FAFAFA',
})

C = {
    'dark':   '#3E1F00',
    'brown':  '#7B4A1E',
    'gold':   '#C8972A',
    'cream':  '#FFF8F0',
    'green':  '#2E7D32',
    'red':    '#C62828',
    'blue':   '#1565C0',
    'purple': '#6A1B9A',
    'teal':   '#00695C',
    'orange': '#E65100',
}
PAL  = [C['dark'], C['gold'], C['brown'], C['teal'], C['purple'],
        C['blue'], C['orange'], C['green'], C['red'], '#546E7A']
CMAP = 'YlOrBr'

FILE = "Coffee Shop Sales.xlsx"

df = pd.read_excel(FILE)
df['revenue']      = df['transaction_qty'] * df['unit_price']
df['month']        = df['transaction_date'].dt.to_period('M').astype(str)
df['month_name']   = df['transaction_date'].dt.strftime('%b %Y')
df['month_num']    = df['transaction_date'].dt.month
df['day_of_week']  = df['transaction_date'].dt.day_name()
df['day_num']      = df['transaction_date'].dt.dayofweek
df['hour']         = pd.to_datetime(df['transaction_time'], format='%H:%M:%S').dt.hour
df['week']         = df['transaction_date'].dt.isocalendar().week.astype(int)
df['date_str']     = df['transaction_date'].dt.date
df['is_weekend']   = df['day_num'].isin([5, 6])
df['price_bucket'] = pd.cut(df['unit_price'],
                             bins=[0,2,4,6,10,50],
                             labels=['<$2','$2-4','$4-6','$6-10','>$10'])

DOW_ORDER = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']


monthly = (df.groupby(['month','month_name'])
             .agg(revenue=('revenue','sum'),
                  orders=('transaction_id','count'),
                  units=('transaction_qty','sum'))
             .reset_index().sort_values('month'))
monthly['mom_pct'] = monthly['revenue'].pct_change() * 100

total_rev   = df['revenue'].sum()
total_ord   = len(df)
avg_ord_val = df['revenue'].mean()
total_units = df['transaction_qty'].sum()
best_month  = monthly.loc[monthly['revenue'].idxmax(), 'month_name']
growth_pct  = (monthly['revenue'].iloc[-1] - monthly['revenue'].iloc[0]) / monthly['revenue'].iloc[0] * 100

fig = plt.figure(figsize=(18, 10), facecolor='#1A0A00')
fig.suptitle('☕  COFFEE SHOP SALES — EXECUTIVE DASHBOARD  |  Jan–Jun 2023',
             fontsize=16, fontweight='bold', color='white', y=0.97)

gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.5, wspace=0.4)

kpis = [
    ("💰 Total Revenue",       f"${total_rev:,.0f}",    C['gold']),
    ("🧾 Transactions",         f"{total_ord:,}",        C['teal']),
    ("🛒 Avg Order Value",      f"${avg_ord_val:.2f}",   C['green']),
    ("📈 Revenue Growth",       f"+{growth_pct:.1f}%",   C['orange']),
]
for i, (label, value, color) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor('#2C1200')
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.axis('off')
    ax.text(0.5, 0.72, value, ha='center', va='center',
            fontsize=22, fontweight='bold', color=color, transform=ax.transAxes)
    ax.text(0.5, 0.28, label, ha='center', va='center',
            fontsize=9, color='#CCCCCC', transform=ax.transAxes)
    for spine in ax.spines.values():
        spine.set_edgecolor(color)

ax_line = fig.add_subplot(gs[1, :2])
ax_line.set_facecolor('#1A0A00')
ax_line.plot(monthly['month_name'], monthly['revenue']/1000,
             color=C['gold'], linewidth=3, marker='o', markersize=8, zorder=3)
ax_line.fill_between(range(len(monthly)), monthly['revenue']/1000,
                     alpha=0.25, color=C['gold'])
ax_line.set_title('Monthly Revenue Trend ($K)', color='white')
ax_line.tick_params(colors='white'); ax_line.yaxis.label.set_color('white')
ax_line.spines['bottom'].set_color('#555'); ax_line.spines['left'].set_color('#555')
ax_line.set_facecolor('#1A0A00')
for val, x in zip(monthly['revenue']/1000, range(len(monthly))):
    ax_line.text(x, val+1, f'${val:.0f}K', ha='center', fontsize=8, color=C['gold'])
ax_line.set_xticks(range(len(monthly)))
ax_line.set_xticklabels(monthly['month_name'], rotation=20, color='white', fontsize=8)
ax_line.tick_params(axis='y', colors='white')

ax_donut = fig.add_subplot(gs[1, 2])
ax_donut.set_facecolor('#1A0A00')
store_rev = df.groupby('store_location')['revenue'].sum()
wedges, texts, autotexts = ax_donut.pie(
    store_rev, labels=store_rev.index, autopct='%1.1f%%',
    colors=[C['gold'], C['brown'], C['teal']],
    wedgeprops=dict(width=0.55, edgecolor='#1A0A00', linewidth=2),
    startangle=90, pctdistance=0.75)
for t in texts: t.set_color('white'); t.set_fontsize(8)
for a in autotexts: a.set_color('white'); a.set_fontweight('bold'); a.set_fontsize(8)
ax_donut.set_title('Revenue by Store', color='white')

ax_cat = fig.add_subplot(gs[1, 3])
ax_cat.set_facecolor('#1A0A00')
cat_rev = df.groupby('product_category')['revenue'].sum().sort_values(ascending=True).tail(5)
bars = ax_cat.barh(cat_rev.index, cat_rev.values/1000,
                   color=[C['dark'], C['brown'], C['gold'], C['orange'], C['teal']])
ax_cat.set_title('Top 5 Categories ($K)', color='white')
ax_cat.tick_params(colors='white')
ax_cat.spines['bottom'].set_color('#555'); ax_cat.spines['left'].set_color('#555')
for bar, val in zip(bars, cat_rev.values/1000):
    ax_cat.text(val+0.5, bar.get_y()+bar.get_height()/2, f'${val:.0f}K',
                va='center', fontsize=7, color='white')

ax_mom = fig.add_subplot(gs[2, :2])
ax_mom.set_facecolor('#1A0A00')
mom = monthly.dropna(subset=['mom_pct'])
colors_mom = [C['green'] if v > 0 else C['red'] for v in mom['mom_pct']]
ax_mom.bar(mom['month_name'], mom['mom_pct'], color=colors_mom, edgecolor='#1A0A00')
ax_mom.axhline(0, color='gray', linewidth=1, linestyle='--')
ax_mom.set_title('Month-over-Month Revenue Growth (%)', color='white')
ax_mom.tick_params(colors='white')
ax_mom.spines['bottom'].set_color('#555'); ax_mom.spines['left'].set_color('#555')
for x, v in enumerate(mom['mom_pct']):
    ax_mom.text(x, v+0.5, f'{v:.1f}%', ha='center', fontsize=9,
                fontweight='bold', color=C['green'] if v > 0 else C['red'])
ax_mom.set_xticks(range(len(mom)))
ax_mom.set_xticklabels(mom['month_name'], rotation=20, color='white', fontsize=8)
ax_mom.tick_params(axis='y', colors='white')

ax_heat = fig.add_subplot(gs[2, 2:])
ax_heat.set_facecolor('#1A0A00')
hour_day = df.groupby(['day_of_week','hour'])['orders'].count() if 'orders' in df.columns else \
           df.groupby(['day_of_week','hour']).size().reset_index(name='cnt')
pivot = df.pivot_table(values='revenue', index='day_of_week', columns='hour',
                       aggfunc='sum').reindex(DOW_ORDER)
sns.heatmap(pivot/1000, cmap='YlOrBr', ax=ax_heat, linewidths=0,
            cbar_kws={'shrink':0.8, 'label':'Revenue ($K)'})
ax_heat.set_title('Revenue Heatmap: Day × Hour', color='white')
ax_heat.tick_params(colors='white', labelsize=7)
ax_heat.set_xlabel('Hour', color='white'); ax_heat.set_ylabel('', color='white')

plt.savefig('chart_01_dashboard.png', dpi=150, bbox_inches='tight', facecolor='#1A0A00')
plt.close()


prod = df.groupby('product_type').agg(
    avg_price=('unit_price','mean'),
    total_orders=('transaction_id','count'),
    total_revenue=('revenue','sum'),
    category=('product_category','first')
).reset_index()

cat_list = prod['category'].unique()
cat_colors = {c: PAL[i % len(PAL)] for i, c in enumerate(cat_list)}

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Scatter & Bubble Analysis — Price vs Demand', fontsize=14, fontweight='bold')

ax = axes[0]
for cat, grp in prod.groupby('category'):
    ax.scatter(grp['avg_price'], grp['total_orders'],
               color=cat_colors[cat], s=80, alpha=0.85,
               label=cat, edgecolors='white', linewidth=0.6, zorder=3)
    for _, row in grp.iterrows():
        if row['total_orders'] > 3000 or row['avg_price'] > 15:
            ax.annotate(row['product_type'],
                        (row['avg_price'], row['total_orders']),
                        fontsize=7, xytext=(5,3), textcoords='offset points',
                        color='#333')
z = np.polyfit(prod['avg_price'], prod['total_orders'], 1)
p = np.poly1d(z)
x_line = np.linspace(prod['avg_price'].min(), prod['avg_price'].max(), 100)
ax.plot(x_line, p(x_line), '--', color=C['red'], linewidth=1.5,
        alpha=0.7, label='Trend')
ax.set_xlabel('Average Unit Price ($)')
ax.set_ylabel('Total Orders')
ax.set_title('Avg Price vs Total Orders\n(coloured by category)')
ax.legend(fontsize=7, loc='upper right', framealpha=0.7)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x:.0f}'))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'{x/1000:.0f}K'))

ax2 = axes[1]
bubble_size = (prod['total_orders'] / prod['total_orders'].max()) * 1500
scatter = ax2.scatter(prod['avg_price'], prod['total_revenue'],
                      s=bubble_size, alpha=0.7,
                      c=[list(cat_list).index(c) for c in prod['category']],
                      cmap='YlOrBr', edgecolors='white', linewidth=0.8)
for _, row in prod.iterrows():
    if row['total_revenue'] > 30000:
        ax2.annotate(row['product_type'],
                     (row['avg_price'], row['total_revenue']),
                     fontsize=7, xytext=(5,3), textcoords='offset points')
ax2.set_xlabel('Average Unit Price ($)')
ax2.set_ylabel('Total Revenue ($)')
ax2.set_title('Bubble Chart: Price vs Revenue\n(bubble size = order volume)')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x/1000:.0f}K'))
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x:.0f}'))
for size_label, orders in [('1K orders', 1000), ('5K orders', 5000), ('15K orders', 15000)]:
    ax2.scatter([], [], s=(orders/prod['total_orders'].max())*1500,
                color='gray', alpha=0.5, label=size_label)
ax2.legend(fontsize=8, loc='upper right')

plt.tight_layout()
plt.savefig('chart_02_scatter_bubble.png', dpi=150, bbox_inches='tight')
plt.close()


fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('📊 Customer Preference Poll — What Do People Order?',
             fontsize=14, fontweight='bold', color=C['dark'])

ax = axes[0, 0]
cat_orders = df.groupby('product_category')['transaction_id'].count().sort_values(ascending=True)
cat_pct = cat_orders / cat_orders.sum() * 100
colors_cat = sns.color_palette("YlOrBr_r", n_colors=len(cat_pct))
bars = ax.barh(cat_pct.index, cat_pct.values,
               color=colors_cat, height=0.6, edgecolor='white')
ax.set_xlim(0, cat_pct.max() * 1.25)
ax.set_title('Which Category Do Customers Order Most?\n(% of total orders)', fontweight='bold')
ax.set_xlabel('Share of Orders (%)')
ax.axvline(0, color='gray', linewidth=0.5)
for bar, val in zip(bars, cat_pct.values):
    ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
            f'  {val:.1f}%', va='center', fontsize=9, fontweight='bold',
            color=C['dark'])
ax.tick_params(axis='y', labelsize=9)

ax2 = axes[0, 1]
qty_counts = df['transaction_qty'].value_counts().sort_index()
qty_pct = qty_counts / qty_counts.sum() * 100
poll_colors = [C['dark'], C['gold'], C['brown'], C['teal'], C['purple'], C['orange']]
bars2 = ax2.bar([f'{q} item{"s" if q>1 else ""}' for q in qty_counts.index],
                qty_pct.values, color=poll_colors[:len(qty_counts)],
                edgecolor='white', width=0.6)
ax2.set_title('How Many Items Per Transaction?\n(poll: % of transactions)', fontweight='bold')
ax2.set_ylabel('% of Transactions')
ax2.set_ylim(0, qty_pct.max() * 1.2)
for bar, val in zip(bars2, qty_pct.values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold', color=C['dark'])

ax3 = axes[1, 0]
price_poll = df.groupby('price_bucket', observed=True)['transaction_id'].count()
price_pct = price_poll / price_poll.sum() * 100
bar_colors = [C['green'], C['gold'], C['orange'], C['red'], C['purple']]
bars3 = ax3.bar(price_pct.index, price_pct.values,
                color=bar_colors[:len(price_pct)], edgecolor='white', width=0.6)
ax3.set_title('Price Sensitivity — What Price Range Sells Most?\n(% of all orders)',
              fontweight='bold')
ax3.set_xlabel('Unit Price Range')
ax3.set_ylabel('% of Orders')
ax3.set_ylim(0, price_pct.max() * 1.25)
for bar, val in zip(bars3, price_pct.values):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold', color=C['dark'])

ax4 = axes[1, 1]
wknd = df.groupby('is_weekend').agg(
    orders=('transaction_id','count'),
    revenue=('revenue','sum')).reset_index()
wknd['label'] = wknd['is_weekend'].map({False:'Weekday\n(Mon–Fri)', True:'Weekend\n(Sat–Sun)'})
wknd['days'] = wknd['is_weekend'].map({False: 5, True: 2})
wknd['orders_per_day'] = wknd['orders'] / wknd['days']

x = np.arange(2)
width = 0.35
bars4a = ax4.bar(x - width/2, wknd['orders']/1000, width,
                 label='Total Orders (K)', color=[C['dark'], C['gold']], edgecolor='white')
ax4b = ax4.twinx()
bars4b = ax4b.bar(x + width/2, wknd['orders_per_day'],
                  width, label='Orders/Day', color=[C['teal'], C['orange']],
                  edgecolor='white', alpha=0.85)
ax4.set_xticks(x)
ax4.set_xticklabels(wknd['label'])
ax4.set_ylabel('Total Orders (thousands)')
ax4b.set_ylabel('Orders per Day')
ax4.set_title('Weekday vs Weekend:\nTotal Orders vs Daily Rate', fontweight='bold')
lines1, labels1 = ax4.get_legend_handles_labels()
lines2, labels2 = ax4b.get_legend_handles_labels()
ax4.legend(lines1+lines2, labels1+labels2, loc='upper right', fontsize=8)
for bar, val in zip(bars4a, wknd['orders']/1000):
    ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
             f'{val:.1f}K', ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('chart_03_poll_survey.png', dpi=150, bbox_inches='tight')
plt.close()


monthly_cat = df.groupby(['month_name','month','product_category'])['revenue'].sum().reset_index()
pivot_mc = monthly_cat.pivot_table(values='revenue', index=['month','month_name'],
                                   columns='product_category', fill_value=0).reset_index()
pivot_mc = pivot_mc.sort_values('month')
months_label = pivot_mc['month_name'].tolist()
cat_cols = [c for c in pivot_mc.columns if c not in ['month','month_name']]

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle('Monthly Revenue Breakdown by Product Category', fontsize=14, fontweight='bold')

bottom = np.zeros(len(pivot_mc))
for i, cat in enumerate(cat_cols):
    vals = pivot_mc[cat].values
    axes[0].bar(months_label, vals, bottom=bottom,
                label=cat, color=PAL[i % len(PAL)], edgecolor='white', linewidth=0.5)
    bottom += vals
axes[0].set_title('Absolute Revenue ($) — Stacked by Category', fontweight='bold')
axes[0].set_ylabel('Revenue ($)')
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x/1000:.0f}K'))
axes[0].legend(loc='upper left', fontsize=8, framealpha=0.8, ncol=2)
axes[0].tick_params(axis='x', rotation=20)

pivot_pct = pivot_mc[cat_cols].div(pivot_mc[cat_cols].sum(axis=1), axis=0) * 100
bottom2 = np.zeros(len(pivot_pct))
for i, cat in enumerate(cat_cols):
    vals = pivot_pct[cat].values
    axes[1].bar(months_label, vals, bottom=bottom2,
                label=cat, color=PAL[i % len(PAL)], edgecolor='white', linewidth=0.5)
    bottom2 += vals
axes[1].set_title('100% Stacked — Category Share per Month', fontweight='bold')
axes[1].set_ylabel('Share (%)')
axes[1].set_ylim(0, 100)
axes[1].legend(loc='upper left', fontsize=8, framealpha=0.8, ncol=2)
axes[1].tick_params(axis='x', rotation=20)

plt.tight_layout()
plt.savefig('chart_04_stacked_bar.png', dpi=150, bbox_inches='tight')
plt.close()


fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Revenue Distribution Analysis — Box & Violin Plots', fontsize=14, fontweight='bold')

ax = axes[0, 0]
store_data = [df[df['store_location']==s]['revenue'].values
              for s in df['store_location'].unique()]
store_names = df['store_location'].unique().tolist()
bp = ax.boxplot(store_data, labels=store_names, patch_artist=True,
                medianprops=dict(color='white', linewidth=2),
                flierprops=dict(marker='o', markersize=2, alpha=0.3))
for patch, color in zip(bp['boxes'], [C['dark'], C['gold'], C['brown']]):
    patch.set_facecolor(color); patch.set_alpha(0.8)
ax.set_title('Transaction Revenue by Store', fontweight='bold')
ax.set_ylabel('Revenue per Transaction ($)')
ax.tick_params(axis='x', rotation=15)

ax2 = axes[0, 1]
dow_data  = [df[df['day_of_week']==d]['revenue'].values for d in DOW_ORDER]
parts = ax2.violinplot(dow_data, positions=range(7), showmedians=True,
                       showextrema=True)
for i, pc in enumerate(parts['bodies']):
    pc.set_facecolor(PAL[i % len(PAL)]); pc.set_alpha(0.8)
parts['cmedians'].set_color('white'); parts['cmedians'].set_linewidth(2)
ax2.set_xticks(range(7))
ax2.set_xticklabels([d[:3] for d in DOW_ORDER])
ax2.set_title('Revenue Distribution by Day of Week\n(violin plot)', fontweight='bold')
ax2.set_ylabel('Revenue per Transaction ($)')
ax2.set_ylim(0, 50)

ax3 = axes[1, 0]
top5_cats = df.groupby('product_category')['revenue'].sum().nlargest(5).index.tolist()
cat_rev_data = [df[df['product_category']==c]['revenue'].values for c in top5_cats]
bp3 = ax3.boxplot(cat_rev_data, labels=[c.replace(' ','\n') for c in top5_cats],
                  patch_artist=True,
                  medianprops=dict(color='white', linewidth=2),
                  flierprops=dict(marker='.', markersize=2, alpha=0.2))
for patch, color in zip(bp3['boxes'], PAL[:5]):
    patch.set_facecolor(color); patch.set_alpha(0.8)
ax3.set_title('Revenue Distribution — Top 5 Categories', fontweight='bold')
ax3.set_ylabel('Revenue per Transaction ($)')

ax4 = axes[1, 1]
peak_hours = range(7, 13)
hour_data = [df[df['hour']==h]['revenue'].values for h in peak_hours]
parts4 = ax4.violinplot(hour_data, positions=list(peak_hours), showmedians=True)
for i, pc in enumerate(parts4['bodies']):
    pc.set_facecolor(C['gold']); pc.set_alpha(0.75)
parts4['cmedians'].set_color(C['dark']); parts4['cmedians'].set_linewidth(2)
ax4.set_title('Revenue Distribution by Peak Hour (7am–12pm)\n(violin plot)', fontweight='bold')
ax4.set_xlabel('Hour of Day')
ax4.set_ylabel('Revenue per Transaction ($)')
ax4.set_ylim(0, 50)

plt.tight_layout()
plt.savefig('chart_05_box_violin.png', dpi=150, bbox_inches='tight')
plt.close()


fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Distribution Analysis — Histograms & KDE', fontsize=14, fontweight='bold')

ax = axes[0, 0]
rev_data = df['revenue'].clip(upper=30)
ax.hist(rev_data, bins=40, color=C['gold'], edgecolor='white',
        alpha=0.85, density=True)
rev_data.plot.kde(ax=ax, color=C['dark'], linewidth=2, label='KDE')
ax.axvline(df['revenue'].mean(), color=C['red'], linestyle='--',
           linewidth=1.5, label=f'Mean ${df["revenue"].mean():.2f}')
ax.axvline(df['revenue'].median(), color=C['green'], linestyle='--',
           linewidth=1.5, label=f'Median ${df["revenue"].median():.2f}')
ax.set_title('Transaction Revenue Distribution\n(clipped at $30)', fontweight='bold')
ax.set_xlabel('Revenue ($)')
ax.set_ylabel('Density')
ax.legend(fontsize=9)

ax2 = axes[0, 1]
ax2.hist(df['unit_price'], bins=35, color=C['brown'], edgecolor='white', alpha=0.85)
ax2.set_title('Unit Price Distribution\n(all transactions)', fontweight='bold')
ax2.set_xlabel('Unit Price ($)')
ax2.set_ylabel('Frequency')
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x:.0f}'))

ax3 = axes[1, 0]
daily = df.groupby('date_str')['revenue'].sum()
ax3.hist(daily.values, bins=30, color=C['teal'], edgecolor='white', alpha=0.85, density=True)
daily_series = pd.Series(daily.values)
daily_series.plot.kde(ax=ax3, color=C['dark'], linewidth=2)
ax3.axvline(daily.mean(), color=C['red'], linestyle='--',
            linewidth=1.5, label=f'Mean ${daily.mean():,.0f}')
ax3.set_title('Daily Revenue Distribution', fontweight='bold')
ax3.set_xlabel('Daily Revenue ($)')
ax3.set_ylabel('Density')
ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x/1000:.0f}K'))
ax3.legend()

ax4 = axes[1, 1]
hourly_counts = df.groupby(['date_str','hour']).size().reset_index(name='count')
ax4.hist(hourly_counts['count'], bins=25, color=C['purple'],
         edgecolor='white', alpha=0.85)
ax4.axvline(hourly_counts['count'].mean(), color=C['red'], linestyle='--',
            linewidth=1.5, label=f'Mean {hourly_counts["count"].mean():.1f}')
ax4.set_title('Distribution of Orders per Hour\n(across all days & stores)', fontweight='bold')
ax4.set_xlabel('Orders in a Given Hour')
ax4.set_ylabel('Frequency')
ax4.legend()

plt.tight_layout()
plt.savefig('chart_06_histograms.png', dpi=150, bbox_inches='tight')
plt.close()


daily_rev = df.groupby('date_str')['revenue'].sum().reset_index()
daily_rev = daily_rev.sort_values('date_str')
daily_rev['cumulative'] = daily_rev['revenue'].cumsum()
daily_rev['rolling_7'] = daily_rev['revenue'].rolling(7, min_periods=1).mean()
daily_rev['x'] = range(len(daily_rev))

daily_store = df.groupby(['date_str','store_location'])['revenue'].sum().reset_index()
daily_store = daily_store.sort_values('date_str')

fig, axes = plt.subplots(2, 1, figsize=(16, 10))
fig.suptitle('Revenue Time Series — Area & Trend Charts', fontsize=14, fontweight='bold')

ax = axes[0]
ax.fill_between(range(len(daily_rev)), daily_rev['revenue'],
                alpha=0.4, color=C['gold'], label='Daily Revenue')
ax.plot(range(len(daily_rev)), daily_rev['revenue'],
        color=C['gold'], linewidth=0.8, alpha=0.6)
ax.plot(range(len(daily_rev)), daily_rev['rolling_7'],
        color=C['dark'], linewidth=2.5, label='7-Day Rolling Avg')
tick_pos = list(range(0, len(daily_rev), 15))
ax.set_xticks(tick_pos)
ax.set_xticklabels([str(daily_rev['date_str'].iloc[i]) for i in tick_pos],
                   rotation=30, fontsize=8)
ax.set_title('Daily Revenue with 7-Day Rolling Average', fontweight='bold')
ax.set_ylabel('Revenue ($)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x:,.0f}'))
ax.legend(fontsize=10)

ax2 = axes[1]
stores = df['store_location'].unique()
store_daily = {}
for s in stores:
    sub = daily_store[daily_store['store_location']==s].set_index('date_str')['revenue']
    store_daily[s] = sub

all_dates = sorted(daily_store['date_str'].unique())
store_matrix = pd.DataFrame({s: [store_daily[s].get(d, 0) for d in all_dates]
                               for s in stores})

ax2.stackplot(range(len(all_dates)), [store_matrix[s] for s in stores],
              labels=stores, colors=[C['dark'], C['gold'], C['brown']],
              alpha=0.85)
ax2.set_xticks(tick_pos)
ax2.set_xticklabels([str(all_dates[i]) for i in tick_pos if i < len(all_dates)],
                    rotation=30, fontsize=8)
ax2.set_title('Daily Revenue — Stacked by Store Location', fontweight='bold')
ax2.set_ylabel('Revenue ($)')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x:,.0f}'))
ax2.legend(loc='upper left', fontsize=10)

plt.tight_layout()
plt.savefig('chart_07_area_charts.png', dpi=150, bbox_inches='tight')
plt.close()


numeric_cols = ['transaction_qty', 'unit_price', 'revenue', 'hour', 'day_num', 'month_num']
corr_df = df[numeric_cols].copy()
corr_df.columns = ['Qty','Unit Price','Revenue','Hour','Day','Month']
corr_matrix = corr_df.corr()

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Correlation Analysis', fontsize=14, fontweight='bold')

mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, ax=axes[0], mask=mask,
            square=True, linewidths=1,
            cbar_kws={'shrink':0.8})
axes[0].set_title('Correlation Matrix\n(lower triangle)', fontweight='bold')

pairs = [('Unit Price','Revenue'), ('Qty','Revenue'), ('Hour','Revenue')]
x_vals = [corr_df['Unit Price'], corr_df['Qty'], corr_df['Hour']]
y_vals = [corr_df['Revenue'], corr_df['Revenue'], corr_df['Revenue']]

inner = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=axes[1].get_subplotspec(),
                                          wspace=0.4)
axes[1].remove()
for i, (label, xd, yd) in enumerate(zip(pairs, x_vals, y_vals)):
    ax_s = fig.add_subplot(inner[i])
    sample = min(3000, len(xd))
    idx = np.random.choice(len(xd), sample, replace=False)
    ax_s.scatter(xd.iloc[idx], yd.iloc[idx], alpha=0.15, s=5, color=PAL[i])
    z = np.polyfit(xd.iloc[idx], yd.iloc[idx], 1)
    xl = np.linspace(xd.min(), xd.max(), 100)
    ax_s.plot(xl, np.poly1d(z)(xl), color=C['red'], linewidth=1.5)
    r = corr_df[[label[0], label[1]]].corr().iloc[0,1]
    ax_s.set_title(f'{label[0]} vs\n{label[1]}\nr={r:.2f}', fontsize=9, fontweight='bold')
    ax_s.set_xlabel(label[0], fontsize=8)
    ax_s.set_ylabel(label[1], fontsize=8)
    ax_s.tick_params(labelsize=7)

plt.savefig('chart_08_correlation.png', dpi=150, bbox_inches='tight')
plt.close()


cat_rev = df.groupby('product_category')['revenue'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(14, 6))
fig.suptitle('Revenue Waterfall — Category Contribution Build-up',
             fontsize=14, fontweight='bold')

running = 0
x_pos = list(range(len(cat_rev))) + [len(cat_rev)]
labels = list(cat_rev.index) + ['TOTAL']
bottoms = []
heights = []

for val in cat_rev.values:
    bottoms.append(running)
    heights.append(val)
    running += val
bottoms.append(0)
heights.append(running)

bar_colors = PAL[:len(cat_rev)] + [C['dark']]
for i, (b, h, label, color) in enumerate(zip(bottoms, heights, labels, bar_colors)):
    is_total = (i == len(cat_rev))
    bar = ax.bar(i, h, bottom=b if not is_total else 0,
                 color=color, edgecolor='white', linewidth=1.5,
                 width=0.6, alpha=0.9)
    ax.text(i, (b + h/2) if not is_total else h/2,
            f'${h/1000:.0f}K', ha='center', va='center',
            fontsize=9, fontweight='bold', color='white')
    if not is_total and i < len(cat_rev)-1:
        next_b = bottoms[i+1]
        ax.plot([i+0.3, i+0.7], [b+h, b+h], color='gray',
                linewidth=1, linestyle='--')

ax.set_xticks(x_pos)
ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=9)
ax.set_ylabel('Revenue ($)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x/1000:.0f}K'))
ax.set_title('Each category adds to total revenue', fontsize=10, style='italic')

plt.tight_layout()
plt.savefig('chart_09_waterfall.png', dpi=150, bbox_inches='tight')
plt.close()


store_monthly = (df.groupby(['store_location','month','month_name'])
                   .agg(revenue=('revenue','sum'),
                        orders=('transaction_id','count'))
                   .reset_index().sort_values('month'))

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Store-Level Monthly Comparison', fontsize=14, fontweight='bold')

ax = axes[0]
store_colors = {s: c for s, c in zip(df['store_location'].unique(),
                                      [C['dark'], C['gold'], C['brown']])}
for store, grp in store_monthly.groupby('store_location'):
    ax.plot(grp['month_name'], grp['revenue']/1000,
            marker='o', linewidth=2.5, markersize=8,
            color=store_colors[store], label=store)
    for _, row in grp.iterrows():
        ax.annotate(f'${row["revenue"]/1000:.0f}K',
                    (row['month_name'], row['revenue']/1000),
                    textcoords='offset points', xytext=(0, 8),
                    ha='center', fontsize=7, color=store_colors[store])
ax.set_title('Monthly Revenue by Store ($K)', fontweight='bold')
ax.set_ylabel('Revenue ($K)')
ax.legend(title='Store', fontsize=9)
ax.tick_params(axis='x', rotation=20)

ax2 = axes[1]
months_u = store_monthly['month_name'].unique()
stores_u = store_monthly['store_location'].unique()
x = np.arange(len(months_u))
width = 0.28
for i, (store, grp) in enumerate(store_monthly.groupby('store_location')):
    grp = grp.sort_values('month')
    offset = (i - 1) * width
    bars = ax2.bar(x + offset, grp['orders'], width,
                   label=store, color=list(store_colors.values())[i],
                   edgecolor='white', linewidth=0.5)
ax2.set_title('Monthly Orders by Store', fontweight='bold')
ax2.set_ylabel('Number of Orders')
ax2.set_xticks(x)
ax2.set_xticklabels(months_u, rotation=20, fontsize=9)
ax2.legend(fontsize=9)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'{x/1000:.0f}K'))

plt.tight_layout()
plt.savefig('chart_10_store_comparison.png', dpi=150, bbox_inches='tight')
plt.close()


fig, axes = plt.subplots(1, 3, figsize=(20, 6))
fig.suptitle('Revenue Heatmap Analysis', fontsize=14, fontweight='bold')

pivot1 = df.pivot_table(values='transaction_id', index='day_of_week',
                        columns='hour', aggfunc='count').reindex(DOW_ORDER)
sns.heatmap(pivot1, cmap='YlOrBr', ax=axes[0], linewidths=0.3,
            cbar_kws={'label':'Orders'}, fmt='.0f', annot=False)
axes[0].set_title('Orders: Day of Week × Hour', fontweight='bold')
axes[0].set_xlabel('Hour of Day')

pivot2 = df.pivot_table(values='revenue', index='month_name',
                        columns='product_category', aggfunc='sum')
pivot2 = pivot2.reindex(df.groupby(['month','month_name']).size().reset_index()
                          .sort_values('month')['month_name'].tolist())
sns.heatmap(pivot2/1000, cmap='YlOrBr', ax=axes[1], linewidths=0.3,
            cbar_kws={'label':'Revenue ($K)'}, annot=True, fmt='.0f',
            annot_kws={'size': 8})
axes[1].set_title('Revenue ($K): Month × Category', fontweight='bold')
axes[1].set_xlabel('')
axes[1].tick_params(axis='x', rotation=30, labelsize=7)

pivot3 = df.pivot_table(values='revenue', index='store_location',
                        columns='product_category', aggfunc='sum')
sns.heatmap(pivot3/1000, cmap='YlOrBr', ax=axes[2], linewidths=0.5,
            cbar_kws={'label':'Revenue ($K)'}, annot=True, fmt='.0f',
            annot_kws={'size': 9})
axes[2].set_title('Revenue ($K): Store × Category', fontweight='bold')
axes[2].set_xlabel('')
axes[2].tick_params(axis='x', rotation=30, labelsize=8)

plt.tight_layout()
plt.savefig('chart_11_heatmaps.png', dpi=150, bbox_inches='tight')
plt.close()


fig, axes = plt.subplots(1, 3, figsize=(18, 7))
fig.suptitle('Revenue Share Analysis — Donut & Pie Charts', fontsize=14, fontweight='bold')

def make_donut(ax, labels, values, title, colors, explode=None):
    exp = explode if explode else [0.03]*len(values)
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct='%1.1f%%',
        colors=colors, startangle=90, explode=exp,
        wedgeprops=dict(width=0.6, edgecolor='white', linewidth=2),
        pctdistance=0.75)
    for t in texts: t.set_fontsize(9)
    for a in autotexts: a.set_fontweight('bold'); a.set_fontsize(9)
    ax.set_title(title, fontweight='bold', pad=12)

cat_r = df.groupby('product_category')['revenue'].sum().sort_values(ascending=False)
make_donut(axes[0], cat_r.index, cat_r.values,
           'Revenue by Category', PAL[:len(cat_r)])

store_r = df.groupby('store_location')['revenue'].sum()
make_donut(axes[1], store_r.index, store_r.values,
           'Revenue by Store', [C['dark'], C['gold'], C['brown']],
           explode=[0.05, 0.02, 0.02])

wknd_r = df.groupby('is_weekend')['revenue'].sum()
wknd_labels = [f'Weekday (Mon–Fri)\n{wknd_r[False]/1000:.0f}K',
               f'Weekend (Sat–Sun)\n{wknd_r[True]/1000:.0f}K']
axes[2].pie(wknd_r.values, labels=wknd_labels,
            autopct='%1.1f%%', colors=[C['dark'], C['gold']],
            startangle=90, explode=[0.03, 0.06],
            wedgeprops=dict(edgecolor='white', linewidth=2),
            pctdistance=0.75)
axes[2].set_title('Weekday vs Weekend Revenue', fontweight='bold', pad=12)

plt.tight_layout()
plt.savefig('chart_12_donut_pie.png', dpi=150, bbox_inches='tight')
plt.close()


prod_rev = df.groupby('product_type').agg(
    revenue=('revenue','sum'),
    orders=('transaction_id','count')).reset_index().sort_values('revenue', ascending=False).head(15)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('Top 15 Products — Revenue Ranking', fontsize=14, fontweight='bold')

ax = axes[0]
colors_bar = [C['gold'] if i == 0 else C['dark'] if i < 3 else C['brown']
              for i in range(len(prod_rev))]
bars = ax.barh(prod_rev['product_type'][::-1], prod_rev['revenue'][::-1]/1000,
               color=colors_bar[::-1], edgecolor='white', height=0.65)
ax.set_title('Top 15 Products by Revenue ($K)', fontweight='bold')
ax.set_xlabel('Revenue ($K)')
for bar, val in zip(bars, prod_rev['revenue'][::-1]/1000):
    ax.text(val + 0.3, bar.get_y()+bar.get_height()/2,
            f'${val:.0f}K', va='center', fontsize=8, fontweight='bold')
ax.set_xlim(0, prod_rev['revenue'].max()/1000 * 1.2)

ax2 = axes[1]
prod_aov = df.groupby('product_type').agg(
    aov=('revenue','mean'), orders=('transaction_id','count')
).reset_index().sort_values('aov', ascending=False).head(15)
y_pos = range(len(prod_aov))
ax2.hlines(list(y_pos), 0, prod_aov['aov'].values,
           colors=C['brown'], linewidth=2, alpha=0.6)
ax2.scatter(prod_aov['aov'], list(y_pos),
            s=[o/30 for o in prod_aov['orders']], color=C['gold'],
            zorder=5, edgecolors=C['dark'], linewidth=0.8)
ax2.set_yticks(list(y_pos))
ax2.set_yticklabels(prod_aov['product_type'], fontsize=8)
ax2.set_xlabel('Avg Revenue per Transaction ($)')
ax2.set_title('Avg Order Value — Lollipop Chart\n(dot size = order volume)', fontweight='bold')
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x:.1f}'))

plt.tight_layout()
plt.savefig('chart_13_product_ranking.png', dpi=150, bbox_inches='tight')
plt.close()


hourly = df.groupby('hour').agg(
    orders=('transaction_id','count'),
    revenue=('revenue','sum')).reset_index()
dow_rev = df.groupby(['day_of_week','day_num']).agg(
    orders=('transaction_id','count'),
    revenue=('revenue','sum')).reset_index().sort_values('day_num')

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Traffic & Revenue Pattern Deep Dive', fontsize=14, fontweight='bold')

ax = axes[0, 0]
hour_colors = [C['red'] if v > hourly['orders'].mean()*1.2
               else C['gold'] if v > hourly['orders'].mean()
               else C['brown'] for v in hourly['orders']]
ax.bar(hourly['hour'], hourly['orders'], color=hour_colors, edgecolor='white')
ax.axhline(hourly['orders'].mean(), color='gray', linestyle='--', linewidth=1.5,
           label=f'Average ({hourly["orders"].mean():,.0f})')
ax.set_title('Hourly Order Volume\n🔴 Peak  🟡 Above Avg  🟫 Below Avg', fontweight='bold')
ax.set_xlabel('Hour (24h)')
ax.set_ylabel('Total Orders')
ax.legend(); ax.set_xticks(range(0, 24, 2))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'{x/1000:.0f}K'))

ax2 = axes[0, 1]
ax2b = ax2.twinx()
ax2.bar(hourly['hour'], hourly['revenue']/1000, color=C['gold'],
        alpha=0.7, label='Revenue ($K)')
ax2b.plot(hourly['hour'], hourly['orders'],
          color=C['dark'], linewidth=2.5, marker='o', markersize=5,
          label='Orders')
ax2.set_xlabel('Hour')
ax2.set_ylabel('Revenue ($K)', color=C['gold'])
ax2b.set_ylabel('Orders', color=C['dark'])
ax2.set_title('Revenue vs Orders by Hour', fontweight='bold')
ax2.set_xticks(range(0, 24, 2))
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2b.get_legend_handles_labels()
ax2.legend(lines1+lines2, labels1+labels2, fontsize=9)

ax3 = axes[1, 0]
dow_colors_list = [C['gold'] if d in ['Saturday','Sunday'] else C['dark']
                   for d in dow_rev['day_of_week']]
bars3 = ax3.bar([d[:3] for d in dow_rev['day_of_week']], dow_rev['orders'],
                color=dow_colors_list, edgecolor='white')
ax3.set_title('Total Orders by Day\n(gold = weekends)', fontweight='bold')
ax3.set_ylabel('Orders')
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'{x/1000:.0f}K'))
for bar, val in zip(bars3, dow_rev['orders']):
    ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+50,
             f'{val/1000:.1f}K', ha='center', fontsize=8, fontweight='bold')

ax4 = fig.add_subplot(2, 2, 4, projection='polar')
theta = np.linspace(0, 2*np.pi, 24, endpoint=False)
r = hourly.set_index('hour').reindex(range(24), fill_value=0)['orders'].values
theta_closed = np.append(theta, theta[0])
r_closed = np.append(r, r[0])
ax4.plot(theta_closed, r_closed, color=C['gold'], linewidth=2.5)
ax4.fill(theta_closed, r_closed, alpha=0.25, color=C['gold'])
ax4.set_xticks(theta)
ax4.set_xticklabels([f'{h}h' for h in range(24)], fontsize=7)
ax4.set_title('24-Hour Order\nRadar (Polar)', fontweight='bold', pad=20)
ax4.set_facecolor('#FFF8F0')

plt.tight_layout()
plt.savefig('chart_14_traffic.png', dpi=150, bbox_inches='tight')
plt.close()


fig = plt.figure(figsize=(18, 11), facecolor='#1A0A00')
fig.text(0.5, 0.96, '☕  KEY INSIGHTS & FINDINGS  —  Coffee Shop Sales 2023',
         ha='center', fontsize=16, fontweight='bold', color=C['gold'])
fig.text(0.5, 0.93, '149,116 Transactions | 3 Stores | Jan–Jun 2023 | $698,812 Total Revenue',
         ha='center', fontsize=10, color='#CCCCCC')

insights = [
    ("📈", "103.8%", "Revenue Growth\nJan → Jun"),
    ("🏆", "Hell's\nKitchen", "Top Store by\nRevenue"),
    ("☕", "Barista\nEspresso", "#1 Product\nby Revenue"),
    ("⏰", "10:00 AM", "Peak Hour\nDaily"),
    ("📅", "Friday", "Busiest Day\nof Week"),
    ("💰", "$4.72", "Best Avg\nOrder Value"),
    ("🌿", "Coffee\n38.6%", "Top Category\nShare"),
    ("📦", "$3.38", "Average\nUnit Price"),
]

for i, (icon, value, label) in enumerate(insights):
    x = 0.06 + (i % 4) * 0.235
    y = 0.72 if i < 4 else 0.46
    ax = fig.add_axes([x, y, 0.19, 0.18])
    ax.set_facecolor('#2C1200')
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    ax.text(0.5, 0.82, icon, ha='center', va='center', fontsize=20,
            transform=ax.transAxes)
    ax.text(0.5, 0.52, value, ha='center', va='center', fontsize=16,
            fontweight='bold', color=C['gold'], transform=ax.transAxes)
    ax.text(0.5, 0.22, label, ha='center', va='center', fontsize=9,
            color='#CCCCCC', transform=ax.transAxes, linespacing=1.4)
    for spine in ax.spines.values():
        spine.set_edgecolor(C['gold']); spine.set_linewidth(1.5)

ax_b1 = fig.add_axes([0.04, 0.08, 0.28, 0.28])
ax_b1.set_facecolor('#1A0A00')
ax_b1.bar(monthly['month_name'], monthly['revenue']/1000,
          color=C['gold'], edgecolor='#1A0A00')
ax_b1.set_title('Monthly Revenue ($K)', color=C['gold'], fontsize=9, fontweight='bold')
ax_b1.tick_params(colors='#CCCCCC', labelsize=7)
ax_b1.spines['bottom'].set_color('#555'); ax_b1.spines['left'].set_color('#555')
ax_b1.set_facecolor('#1A0A00')
ax_b1.tick_params(axis='x', rotation=30)

ax_b2 = fig.add_axes([0.37, 0.08, 0.25, 0.28])
ax_b2.set_facecolor('#1A0A00')
store_r = df.groupby('store_location')['revenue'].sum()
ax_b2.pie(store_r.values, labels=[s.replace("'s", "s").replace(" ", "\n") for s in store_r.index],
          colors=[C['gold'], C['brown'], C['teal']],
          wedgeprops=dict(width=0.55, edgecolor='#1A0A00'),
          startangle=90, textprops={'color':'white', 'fontsize':8})
ax_b2.set_title('Store Revenue Share', color=C['gold'], fontsize=9, fontweight='bold')

ax_b3 = fig.add_axes([0.66, 0.08, 0.30, 0.28])
ax_b3.set_facecolor('#1A0A00')
top5 = df.groupby('product_type')['revenue'].sum().nlargest(5)
ax_b3.barh(top5.index[::-1], top5.values[::-1]/1000,
           color=[C['gold'], C['brown'], C['dark'], C['teal'], C['orange']])
ax_b3.set_title('Top 5 Products ($K)', color=C['gold'], fontsize=9, fontweight='bold')
ax_b3.tick_params(colors='#CCCCCC', labelsize=7)
ax_b3.spines['bottom'].set_color('#555'); ax_b3.spines['left'].set_color('#555')
ax_b3.set_facecolor('#1A0A00')

plt.savefig('chart_15_insights_infographic.png', dpi=150, bbox_inches='tight',
            facecolor='#1A0A00')
plt.close()
