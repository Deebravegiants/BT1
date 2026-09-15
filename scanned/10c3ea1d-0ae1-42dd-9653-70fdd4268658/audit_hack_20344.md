# [H] 5.2.1 maxStrategistFeeis incorrectly set inAstariaRouter's constructor

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:**

- AstariaRouter.sol#L
- AstariaRouter.sol#L325-L
- PublicVault.sol#L637-L
**Description:** InAstariaRouter's constructor we set themaxStrategistFeeas
s.maxStrategistFee = uint256(50e17);// 5e

But in the filing route we check that this value should not be greater than1e18.


maxStrategistFeeis supposed to set an upper bound for public vaults's strategist vault fee. When a payment
is made for a lien, one calculates the shares to be minted for the strategist based on this value and the interest
amount paid:
function _handleStrategistInterestReward(
VaultData storage s,
uint256 interestPaid
) internal virtual {
if (VAULT_FEE() != uint256(0) && interestPaid > 0) {
uint256 fee = interestPaid.mulWadDown(VAULT_FEE());
uint256 feeInShares = convertToShares(fee);
_mint(owner(), feeInShares);
}
}

Note that we are usingmulWadDown(...)here:

```
F=
```
```
jIf
1018
```
```
k
```
```
parameter description
F fee
f VAULT_FEE()
I interestPaid
```
so we would wantf 1018. Currently, a vault could charge 5 times the interest paid.
**Recommendation:** Perhapss.maxStrategistFeeneeded to be set as 0.5 1018 and not 5 1018

```
s.maxStrategistFee = uint256(5e17);// 0.5 x 1e18, maximum 50%
```
**Astaria:** Fixed in PR 336.
**Spearbit:** Fixed.
