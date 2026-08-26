# [M] Curve Reentrancy Guard will not work if the pool implements a fallback

## Summary
Severity: Medium
Chain: Smart contract
Component: VMEX
Published: 2023-06-30
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/52
Type: hats-finding

## Details
**Github username:** @GalloDaSballo
**Submission hash (on-chain):** 0x452fbd793a0e0e2cc2cfc7197efd6862bac5723a1e389d5fe49c2446782082c3
**Severity:** medium severity

**Description:**
**Description**\
The Reentrancy Guard for Curve is based on the idea that one of the functions called should pass, and passing is a guarantee that the guard was engaged.

That is not the case for Vyper Contract that implement a fallback via `__default__`

The most notable example being Tricrypto on Mainnet: 0xD51a44d3FaE010294C616388b506AcdA1bfAAE46

**Attack Scenario**\
Such a pool is added, reentrancy guard becomes ineffective

**Attachments / POC**

The following POC is written in brownie, just add the contracts and interfaces, then follow the instructions

The goal of the POC is to demonstrate:
1) Tricrypto will not revert if you transfer with some data
2) Fake Curve Pool just implements the fallback
3) If we call a pool with just a fallback, the first try catch in which a function expects no return value will pass, marking the pool as reentrancy safe

## Open Up the Console via
brownie console --network mainnet-fork



## Setup: paste in the console
```python
## Proof fallback is implemented in tricrypto
a[0].transfer("0xD51a44d3FaE010294C616388b506AcdA1bfAAE46", 0, data="0x123")


## Deploy fake pool
fake = FakeCurvePool.deploy({"from": a[0]})
## Proof fallback is working
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/52_
