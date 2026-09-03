# [M] Debt decay interval can be larger than the total duration

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-bond
Published: 2022-11-17
Source: https://github.com/sherlock-audit/2022-11-bond-judging/issues/39
Type: sherlock-finding

## Details
xiaoming90

medium

# Debt decay interval can be larger than the total duration

## Summary

The debt decay interval can be larger than the total duration of the market, which might cause some issues.

## Vulnerability Detail

The following code shows that the `debtDecayInterval` is calculated by multiplying the `params_.depositInterval` by 5 in Line 185.

https://github.com/sherlock-audit/2022-11-bond/blob/main/src/bases/BondBaseSDA.sol#L180

```solidity
File: BondBaseSDA.sol
180:             // The debt decay interval is how long it takes for price to drop to 0 from the last decay timestamp.
181:             // In reality, a 50% drop is likely a guaranteed bond sale. Therefore, debt decay interval needs to be
182:             // long enough to allow a bond to adjust if oversold. It also needs to be some multiple of deposit interval
183:             // because you don't want to go from 100 to 0 during the time frame you expected to sell a single bond.
184:             // A multiple of 5 is a sane default observed from running OP v1 bond markets.
185:             uint32 userDebtDecay = params_.depositInterval * 5;
186:             debtDecayInterval = minDebtDecayInterval > userDebtDecay
187:                 ? minDebtDecayInterval
188:                 : userDebtDecay;
```

The debt decay interval determines how long it takes for the price to drop to 0 from the last decay timestamp. However, it might be possible for a market marker to define a `params_.depositInterval` that results in the derived `debtDecayInterval` being larger than the total duration of the market.

Assume that the parameters of the SDAM:

- params_.depositInterval = 5 days (Debt decay interval - ID in whitepaper)
- secondsToConclusion = 10 days (Total Duration - L in whitepaper)

In this case, the `debtDecayInterval` will end up being 25 days (5 days * 5), which is larger than the `secondsToConclusion `.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bond-judging/issues/39_
