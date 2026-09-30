# [H] YieldMath.sol / Log2: >= or > ?

## Summary
Severity: High
Contest weight: 0.7540
Dataset id: 430
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The V1 version of `YieldMath.sol` contains ”>=” (larger or equal), while the V2 version of `YieldMath.sol` contains ”>” (larger) in the log_2 function. This change doesn’t seem logical and might lead to miss calculations. The difference is present in several adjacent lines.

```solidity
function log_2 (uint128 x)
...
b = b * b >> 127; if (b >= 0x100000000000000000000000000000000) {b >>= 1; l |= 0x1000000000000000000000000000000;}
```

and

```solidity
function log_2(uint128 x)
...
b = b * b >> 127; if(b > 0x100000000000000000000000000000000) {b >>= 1; l |= 0x1000000000000000000000000000000;}
```

Recommend checking which version is the correct version and fix the incorrect version.

That’s entirely my fault, and this is a scary one. We might be having a slightly different or impredictable curve in Pool.sol, and we might notice only after a long while with the Pools being slowly drained. We might never even have found this was the issue.

I would suggest increasing the severity of this issue to High.

**[albertocuestacanada (Yield) Resolved](https://github.com/code-423n4/2021-05-yield-findings/issues/2#issuecomment-854621275):**

[Fix](https://github.com/yieldprotocol/yieldspace-v2/pull/108)

## Recommendation
No recommendation
