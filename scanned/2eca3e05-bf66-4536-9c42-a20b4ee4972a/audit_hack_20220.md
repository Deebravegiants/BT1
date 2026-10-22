# [C] 5.1.2 sweepfunction should prevent Treasury from withdrawing pool’s BPTs

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** AeraVaultV1.sol#L559-L
**Description:** The currentsweep()implementation allows thevaultowner (theTreasury) to sweep any token
owned by the vault including BPTs (Balancer Pool Tokens) that have been minted by the Vault during the pool’s
initialDeposit()function call.
The current vault implementation does not need those BPTs to withdraw funds because they are passed directly
through theAssetManagerflow viawithdraw()/finalize().
Being able to withdraw BPTs would allow the Treasury to:

- Withdraw funds without respecting the time period betweeninitiateFinalization()andfinalize()calls.
- Withdraw funds without respectingValidator allowance()limits.
- Withdraw funds without paying the manager’s fee for the lastwithdraw().
- finalizethe pool, withdrawing all funds and selling valueless BPTs on the market.
- Sell or rent out BPTs andwithdraw()funds afterwards, thus doubling the funds.
Swap fees would not be paid becauseTreasurycould callsetManager(newManager), where the new manager is
someone controlled by the Treasury, subsequently callingsetSwapFee(0)to remove the swap fee, which would be
applied during anexitPool()event.
Note: Once the BPT is retrieved it can also be used to callexitPool(), as themustAllowlistLPscheck is ignored
inexitPool().
**Recommendation:** Add a check on thetokeninput parameter to prevent Treasury from withdrawing the Pool’s
BTP tokens.
**Gauntlet:** Fixed in PR #
**Spearbit:** Acknowledged.
