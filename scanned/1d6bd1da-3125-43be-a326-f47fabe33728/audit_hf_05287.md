# [C] Inability to remove and redeem from vaults with withdrawal issues could result in a bank-run

## Summary
Severity: Critical
Contest weight: 0.0000
Dataset id: 23530
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: When deposits are made to the pUSDeVault, depositedBase is incremented based on the previewed quote amount of USDe underlying the external ERC-4626 vaults; however, these instantaneous preview quotes are not necessarily accurate when compared to the maximum amount that is actually withdrawable. For example, MetaVault::deposit implements calculation of the base USDe assets as:
```solidity
uint baseAssets = IERC4626(token).previewRedeem(tokenAssets);
```
But if the vault has overridden the max withdraw/redeem functions with custom logic that apply some limits then this previewed value could be larger than the actual maximum withdrawable USDe amount. This is possible because the ERC-4626 specification states that preview functions must not account for withdrawal/redemption limits like those returned from maxWithdraw/maxRedeem and should always act as though the redemption would be accepted.

Therefore, given that there is not actually a withdrawal that is executed during the deposit, the depositedBase state is incremented assuming the underlying USDe if fully redeemable, but it is not until removing and redeeming the vault that a revert could arise if the third‑party vault malfunctions or restricts withdrawals. Currently, the only way to pause new deposits for a given vault is by removing the asset from the supported list; however, doing so also triggers a withdrawal of USDe which can fail for the reasons stated above, preventing the asset from being removed.

While none of the externally‑supported vault tokens intend to function with a decrease in share price, it is of course not possible except in very simplistic implementations to rule out the possibility of a smart contract hack in which the underlying USDe is stolen from one of the supported vaults. Combined with the issue above, given that users are free to withdraw into any supported vault token regardless of those that they supplied, full withdraw by other users into unaffected vault tokens (or even if the required USDe is pulled from these vaults by MetaVault::redeemRequiredBaseAssets to process their withdrawals), this could result in a subset of users being left with the bad debt rather than it being amortized.

It is understood that the protocol team has strict criteria for supporting new third‑party vaults, including the need for instant withdrawals, no limits, no cooldowns, and not pausable, though exceptions may be made for partners that maintain robust communication channels regarding development plans and updates.

## Recommendation
Recommended Mitigation: Implement some mechanism to disable new deposits to a vault without having to remove it and (attempt to) fully‑redeem the underlying tokens. To amortize any losses a potential faulty vault, it may be necessary to track the individual vault contributions to depositedBase and so that they can be negated from redemption calculations.
