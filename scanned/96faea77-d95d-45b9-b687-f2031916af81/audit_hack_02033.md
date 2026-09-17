# [H] 6.1 Bypassing Antisnipping Protection

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected

The AntisnippingManager implements logic to protect against so-called liquidity-snipping (Just-in-Time
Liquidity) attacks to prevent attackers from adding much liquidity before a swap and removing it right
afterwards to collect most of the fees while not being exposed to LP risks.

Kyber Network removes the economic incentive of such an attack by locking fees for vestingPeriod
which means an immediate withdrawal of liquidity should set the collected fees to zero.

Note, that AntiSnipAttack protection only comes in play if feeGrowthInsideLast of the position
manager and the feeGrowthInsideLast of the position are not equal:

```
if (feeGrowthInsideLast != pos.feeGrowthInsideLast) {
....
(additionalRTokenOwed, feesBurnable) = AntiSnipAttack.update(
```

### ...

### }

Also, feesBurnable can only be non-zero if liquidity is removed:

```
if (isAddLiquidity) {
....
} else if (_self.feesLocked > 0) {
feesBurnable = (_self.feesLocked * liquidityDelta) / uint256(currentLiquidity);
_self.feesLocked -= feesBurnable;
}
```
Thus, the following attack is possible:

```
1.Attacker sees a huge swap and mints an enormous position
2.Swap occurs.
3.An attacker adds a small amount of liquidity. The position's feeGrowthInsideLast is updated.
However, rTokens are now locked.
4.An attacker removes all his liquidity which does not enter the AntiSnipAttack code since there was
no fee growth. Liquidity is withdrawn and rTokens remain locked.
5.After vestingPeriod has passed the attacker can withdraw the newly generated fees.
```
Even though the attacker does not immediately withdraw the fees, his liquidity came and went
immediately while generating a temporarily locked profit for the attacker.

Code corrected:

In version 3 of the code, the Antisnipping protection logic is triggered on every call of removeLiquidity
function.
