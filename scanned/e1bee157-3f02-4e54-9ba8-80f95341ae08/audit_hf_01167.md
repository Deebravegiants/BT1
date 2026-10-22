# [M] Possible underﬂow of uint128

## Summary
Severity: Medium
Contest weight: 0.0155
Dataset id: 5008
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an integer underflow that occurs when a signed 128‑bit value is directly cast to an unsigned 128‑bit type without first ensuring the value is non‑negative. In the contract, the calculation of a bias term (pt.bias - pt.slope * dt) and a similar user‑specific bias (oldUserPoint.bias - dt * oldUserPoint.slope) are performed using signed arithmetic, but the result is immediately converted to uint128 via int128 casting. If the subtraction yields a negative number, the cast wraps the value to a very large unsigned integer, effectively inflating the stored veSupply or user balance. This happens whenever the time delta (dt) grows large enough that the slope component exceeds the bias, which is a normal condition in many voting‑escrow or reward‑distribution schemes. The underflow is hard to notice because the contract may still compile and run, and the inflated numbers can pass superficial checks; however, downstream accounting that assumes the supply is bounded can produce incorrect rewards, zero payouts, or even allow an attacker to claim more tokens than entitled. From a user perspective the UI may display a massive total supply while individual balances appear unchanged or become zero, leading to confusion such as “my reward claim returns 0” or “my balance disappeared”. The issue was discovered during a manual audit that inspected type conversions and identified the missing max‑zero guard before casting. It belongs to the broader class of signed‑to‑unsigned conversion bugs that cause underflow/overflow. To remediate, the code should compare the signed result with zero and clamp it to a non‑negative value before casting, for example by using Math.maxInt((bias - slope * dt),0) and then converting the clamped result to uint128. This ensures that only valid, non‑negative values are stored, preserving the intended accounting logic and preventing supply inflation or balance loss.

## Recommendation
Do max comparison before converting to uint128:
veSupply[t] = uint128(int128(Math.maxInt((pt.bias - pt.slope * dt), 0)));
uint256 balanceOf = uint128(int128(Math.maxInt((oldUserPoint.bias - dt * oldUserPoint.slope),0)));
