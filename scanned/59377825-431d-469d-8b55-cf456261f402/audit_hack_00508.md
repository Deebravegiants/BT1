# [M] AM/USDT pool incident: The AM/USDT pool on the BSC chain was exploited several hours ago, with estimated losses of approximately $131,000. The root cause

## Summary
Severity: Medium
Target: AM/USDT pool
Loss: $ 131,000
Attack method: Reserve Manipulation Attack
Published: 2026-03-12
Source: https://x.com/Phalcon_xyz/status/2031957703451688970
Type: slowmist-incident

## Details
The AM/USDT pool on the BSC chain was exploited several hours ago, with estimated losses of approximately $131,000. The root cause lies in a vulnerability within the burn mechanism, which was exploited to manipulate the AM reserves in the pool and artificially inflate the token price. The attacker first manipulated the toBurnAmount and then triggered the burn logic after the AM balance in the pool had been adjusted. This drove the AM reserves down to an unnaturally low level, allowing the attacker to sell AM back to the pool at an inflated price to realize a profit.
