# [H] 5.2.9 Add checks toxcall()

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** BridgeFacet.sol#L240-L339, BridgeFacet.sol#L400-L419, Executor.sol#L142-L
**Description:** The functionxcall()does some sanity checks, nevertheless more checks should be added to
prevent issues later on in the use of the protocol.
If_args.recovery== 0then_sendToRecovery()will send funds to the 0 address, effectively losing them.
If_params.agent == 0theforceReceiveLocalcan’t be used and funds might be locked forever.
The_args.params.destinationDomainshould never bes.domain, although this is also implicitly checked via
_mustHaveRemote()assuming a correct configuration.
If_args.params.slippageTolis set to something greater thans.LIQUIDITY_FEE_DENOMINATORthen funds can be
locked asxcall()allows for the user to provide the local asset, avoiding any swap while_handleExecuteLiquid-
ity()inexecute()may attempt to perform a swap on the destination chain.
function xcall(XCallArgs calldata _args) external payable nonReentrant whenNotPaused returns (bytes32) {
// Sanity checks.
...
}


**Recommendation:** Consider adding the following checks:

- recovery != 0.
- agent !=0.
- _args.params.destinationDomain != s.domain.
- _args.params.slippageTol <=s.LIQUIDITY_FEE_DENOMINATOR.
Also doublecheck if any additional checks are useful.
**Connext:** Solved in PR 1536.
**Spearbit:** Verified.
