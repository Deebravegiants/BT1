# [M] curve admin can drain pool via reentrancy (equal to execute emergency withdraw and rug tokenmak fund by third party)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-06-tokemak
Published: 2023-08-30
Source: https://github.com/sherlock-audit/2023-06-tokemak-judging/issues/862
Type: sherlock-finding

## Details
ctf_sec

high

# curve admin can drain pool via reentrancy (equal to execute emergency withdraw and rug tokenmak fund by third party)
## Summary

curve admin can drain pool via reentrancy (equal to execute emergency withdraw and rug tokenmak fund)

## Vulnerability Detail

A few curve liquidity is pool is well in-scope:

```solidity
Curve Pools

Curve stETH/ETH: 0x06325440D014e39736583c165C2963BA99fAf14E
Curve stETH/ETH ng: 0x21E27a5E5513D6e65C4f830167390997aA84843a
Curve stETH/ETH concentrated: 0x828b154032950C8ff7CF8085D841723Db2696056
Curve stETH/frxETH: 0x4d9f9D15101EEC665F77210cB999639f760F831E
Curve rETH/ETH: 0x6c38cE8984a890F5e46e6dF6117C26b3F1EcfC9C
Curve rETH/wstETH: 0x447Ddd4960d9fdBF6af9a790560d0AF76795CB08
Curve rETH/frxETH: 0xbA6c373992AD8ec1f7520E5878E5540Eb36DeBf1
Curve cbETH/ETH: 0x5b6C539b224014A09B3388e51CaAA8e354c959C8
Curve cbETH/frxETH: 0x548E063CE6F3BaC31457E4f5b4e2345286274257
Curve frxETH/ETH: 0xf43211935C781D5ca1a41d2041F397B8A7366C7A
Curve swETH/frxETH: 0xe49AdDc2D1A131c6b8145F0EBa1C946B7198e0BA
```

one of the pool is 0x21E27a5E5513D6e65C4f830167390997aA84843a

https://etherscan.io/address/0x21E27a5E5513D6e65C4f830167390997aA84843a#code#L1121

Admin of curve pools can easily drain curve pools via reentrancy or via the `withdraw_admin_fees` function. 

```solidity
@external
def withdraw_admin_fees():
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2023-06-tokemak-judging/issues/862_
