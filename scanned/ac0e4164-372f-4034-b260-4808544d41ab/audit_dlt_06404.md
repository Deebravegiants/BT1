# [M] Adversary can block any `exit` due to `preCheck` reached `cap` by using flash-loan

## Summary
Severity: Medium
Chain: Smart contract
Component: Origami
Published: 2024-02-25
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/27
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xa152e0fc679f9840949b13a8713252bd1f4f032c33244d6bff807347e639bce3
**Severity:** medium

**Description:**
**Description**

There is a maximum daily`cap` implemented on circuitBreaker contract to prevent any abnormal ovUSDC exits by users.

The `preCheck` will increment current `bucketIndex` amount, beside checking if the sum of rolling period buckets is still under the cap.

```js

File: OrigamiCircuitBreakerAllUsersPerPeriod.sol
098:     function preCheck(address /*onBehalfOf*/, uint256 amount) external override onlyProxy {
...
118:         uint256 _newUtilisation = _currentUtilisation(_nBuckets) + amount;
119:         if (_newUtilisation > cap) revert CapBreached(_newUtilisation, cap);
120: 
121:         // Unchecked is safe since we know the total new utilisation is under the cap.
122:         unchecked {
123:             // slither-disable-next-line weak-prng
124:             buckets[_nextBucketIndex % _nBuckets] += amount;
125:         }
126:     }
```

The issue here is, attacker can flash-loan in order to fill-up the rolling period until it reached its cap.

By using flash-loaned USDC, then `investWithToken` oUSDC and `exitToToken` in a single transaction. This flash loan can trigger `preCheck` and fill up the `cap` easily.

```js
File: OrigamiLendingSupplyManager.sol
146:     function exitToToken(
147:         address account,
148:         IOrigamiInvestment.ExitQuoteData calldata quoteData,
149:         address recipient
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/27_
