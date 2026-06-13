# 巩义燃气 — Home Assistant 自定义集成

将巩义燃气数据接入 Home Assistant。

## 功能

- 燃气余额
- 昨日用气量和燃气费
- 燃气表号
- 地址信息

## 安装

### 通过 HACS

1. 打开 HACS → 自定义仓库 → 添加本仓库 URL
2. 搜索「巩义燃气」并安装
3. 重启 HA
4. 设置 → 集成 → 添加集成 → 搜索「巩义燃气」

### 手动安装

```bash
cd /config/custom_components
git clone https://github.com/your/ha-gongyi-gas.git gongyi_gas
```

重启 HA 后添加集成。

## 配置

需要输入微信 OpenID 和燃气户主姓名（如「王二小」）。

## 实体

| 实体 | 类型 | 说明 |
|---|---|---|
| `sensor.gongyi_gas_balance` | sensor | 燃气余额（元） |
| `sensor.gongyi_gas_yesterday_usage` | sensor | 昨日用气量（m³） |
| `sensor.gongyi_gas_yesterday_fee` | sensor | 昨日燃气费（元） |
| `sensor.gongyi_gas_update_time` | sensor | 更新时间 |
| `sensor.gongyi_gas_meter_number` | sensor | 燃气表号 |
| `sensor.gongyi_gas_address` | sensor | 地址 |

## 数据更新

每 30 分钟自动轮询一次。
