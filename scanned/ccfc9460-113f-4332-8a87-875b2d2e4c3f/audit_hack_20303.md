# [M] 5.2.8 Presence ofdelegatenot enforced

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** BridgeFacet.sol#L395-L414, BridgeFacet.sol#L563-L567, BridgeFacet.sol#L337-L369
**Description:** Adelegateaddress on the destination chain can be used to fix stuck transactions by changing the
slippage limits and by re-executing transactions. However, the presence of adelegateaddress isn't checked in
_xcall().
Note: set to medium risk because tokens could get lost


```
function forceUpdateSlippage(TransferInfo calldata _params, uint256 _slippage) external
,! onlyDelegate(_params) {
}
function execute(ExecuteArgs calldata _args) external nonReentrant whenNotPaused returns (bytes32) {
(bytes32 transferId, DestinationTransferStatus status) = _executeSanityChecks(_args);
}
function _executeSanityChecks(ExecuteArgs calldata _args) private view returns (bytes32,
,! DestinationTransferStatus) {
// If the sender is not approved relayer, revert
if (!s.approvedRelayers[msg.sender] && msg.sender != _args.params.delegate) {
revert BridgeFacet__execute_unapprovedSender();
}
}
```
**Recommendation:** Enforce the presence of adelegateaddress in_xcall(). Or at least document the behavior
explicitly.
**Connext:** Yes, it's always going to be necessary to have a delegate if you want to have a strategy for handling
destination-side slippage conditions being unfavorable. If you don't have one you are taking on the bet that un-
favorable slippage conditions won't be maintained indefinitely. Some groups see having any EOA or multisig that
can impact these parameters as a huge no-no, and requiring one to be defined would be a nonstarter for them.
So we allow to not provide an option on that front, even if it is more risky and could lead to funds being frozen in
transit.
We should add more clarity around this in the documentation though.
**Spearbit:** Acknowledged.
