export function createLineChartDay(ctxId, dates, data) {
    const datasets = Object.keys(data).map((name, index) => {
        let borderColor;
        if (index === 0) {
            borderColor = '#007bff'; // 青色
        } else if (index === 1) {
            borderColor = '#28a745'; // 緑色
        } else {
            borderColor = `#${Math.floor(Math.random() * 16777215).toString(16)}`;
        }
        return {
            label: name,
            data: data[name],
            fill: false,
            borderColor: borderColor,
            borderWidth: 2,
            pointBackgroundColor: '#fff',
            pointRadius: 3, // データポイントの半径を大きくする
            pointHoverRadius: 8, // ホバー時の半径を大きくする
            tension: 0.4
        };
    });

    const ctx = document.getElementById(ctxId).getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true, //凡例
                    labels: {
                        color: '#ccc',
                        font: {
                            size: 10
                        }
                    }
                },
            },
            scales: {
                x: {
                    display: window.innerWidth > 0, //768と指定するとスマホ版のレイアウトに変更可能
                    title: {
                        display: false,
                    },
                    grid: {
                        color: '#333',
                        drawBorder: false,
                    },
                    ticks: {
                        color: '#ccc'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: false,
                    },
                    grid: {
                        color: '#333',
                        drawBorder: false,
                    },
                    ticks: {
                        color: '#ccc'
                    }
                }
            },
            layout: {
                padding: {
                    left: 10,
                    right: 10,
                    top: 20,
                    bottom: 10
                }
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem) {
                        return tooltipItem.dataset.label + ': ' + tooltipItem.raw;
                    }
                }
            }
        }
    });
}

//月ごと人ごとの折れ線グラフ
export function createLineChartMonth(ctxId, dates, data, xAxisLabel = 'Date', yAxisLabel = 'Total Points') {
    const datasets = Object.keys(data).map((name, index) => {
        let borderColor;
        if (index === 0) {
            borderColor = '#007bff'; // 青色
        } else if (index === 1) {
            borderColor = '#28a745'; // 緑色
        } else {
            borderColor = `#${Math.floor(Math.random() * 16777215).toString(16)}`;
        }
        return {
            label: name,
            data: data[name],
            fill: false,
            borderColor: borderColor,
            borderWidth: 2,
            pointBackgroundColor: '#fff',
            pointRadius: 3,
            pointHoverRadius: 8,
            tension: 0.4
        };
    });

    const ctx = document.getElementById(ctxId).getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#ccc',
                        font: {
                            size: 10
                        }
                    }
                },
            },
            scales: {
                x: {
                    display: window.innerWidth > 0, //768と指定するとスマホ版のレイアウトに変更可能
                    title: {
                        display: false,
                    },
                    grid: {
                        color: '#333',
                        drawBorder: false,
                    },
                    ticks: {
                        color: '#ccc'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: false,
                    },
                    grid: {
                        color: '#333',
                        drawBorder: false,
                    },
                    ticks: {
                        color: '#ccc'
                    }
                }
            },
            layout: {
                padding: {
                    left: 10,
                    right: 10,
                    top: 20,
                    bottom: 10
                }
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem) {
                        return tooltipItem.dataset.label + ': ' + tooltipItem.raw;
                    }
                }
            }
        }
    });
}


// <!-- <h2>家事分類区分の円グラフ</h2>
//     <div id="chartsContainer" style="display: flex; flex-wrap: wrap; justify-content: space-around;"> <!-- グラフを表示するコンテナ -->
    
//     <!-- <script>
//         const categoryData = {{ category_data | tojson }}; // Pythonからデータを取得

//         // 名前ごとにカテゴリの合計ポイントを集計
//         const groupedData = categoryData.reduce((acc, data) => {
//             acc[data.name] = acc[data.name] || {};
//             acc[data.name][data.category] = (acc[data.name][data.category] || 0) + data.total_points;
//             return acc;
//         }, {});

//         // 各名前ごとに円グラフを作成
//         for (const name in groupedData) {
//             const ctx = document.createElement('canvas');
//             ctx.width = 50; // 幅を小さく調整
//             ctx.height = 50; // 高さを小さく調整
//             ctx.style.margin = '10px'; // グラフ間の余白を追加
//             document.getElementById('chartsContainer').appendChild(ctx);

//             const labels = Object.keys(groupedData[name]);
//             const dataPoints = labels.map(category => groupedData[name][category]);

//             new Chart(ctx, {
//                 type: 'pie', // 円グラフ
//                 data: {
//                     labels: labels,
//                     datasets: [{
//                         label: `${name}の家事分類区分のポイント`,
//                         data: dataPoints,
//                         backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'], // 色の設定
//                     }]
//                 },
//                 options: {
//                     responsive: true,
//                     plugins: {
//                         legend: {
//                             position: 'top',
//                             display: true // 凡例を常に表示
//                         },
//                         title: {
//                             display: true,
//                             text: `${name}の家事分類区分の円グラフ`
//                         }
//                     },
//                     tooltips: {
//                         callbacks: {
//                             label: function(context) {
//                                 var label = context.dataset.label || '';
//                                 if (label) {
//                                     label += ': ';
//                                 }
//                                 if (context.parsed.y !== null) {
//                                     label += context.parsed.y + '%';
//                                 }
//                                 return label;
//                             }
//                         }
//                     }
//                 }
//             });
//         }
//     </script> --></div>