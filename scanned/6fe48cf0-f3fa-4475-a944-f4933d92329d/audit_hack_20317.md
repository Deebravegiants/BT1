# [M] 5.2.4 Receiverdoes not verify address from the originator chain

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** Receiver.sol#L254 Receiver.sol#L
**Description:** TheReceivercontract is designed to receive the cross-chain call fromlibDiamondaddress on the
destination chain. However, it does not verify the source chain address. An attacker can build a malicious_-
callData. An attacker can steal funds if there are left tokens and there are allowances to theExecutor. Note that
the tokens may be lost in issue: "Arithemetic underflow leading to unexpected revert and loss of funds inReceiver
contract". And there may be allowances toExecutorin issue "Receiverdoesn't always reset allowance"
**Recommendation** : This is a tricky issue. Recommend to fixes other issues, especially making sure to clear the
allowance.
The bridges we're integrating do not always allow users to verify the source address. TakeAmarokfor example,
technically we can verify the sender's address:


```
/// @notice Completes a cross-chain transaction with calldata via Amarok facet on the receiving
,! chain.
/// @dev This function is called from Amarok Router.
/// @param _transferId The unique ID of this transaction (assigned by Amarok)
/// @param _amount the amount of bridged tokens
/// @param _asset the address of the bridged token
/// @param * (unused) the sender of the transaction
/// @param * (unused) the domain ID of the src chain
/// @param _callData The data to execute
function xReceive(
bytes32 _transferId,
uint256 _amount,
address _asset,
address _sender,
uint32,
bytes memory _callData
) external nonReentrant onlyAmarokRouter {
if (_sender != address(diamond) {
revert UnAuthorized();
}
}
```
However, there's a special feature of Amarok. The_senderaddress would beaddress(0)if this is a fast path.
If we revert such transactions, all the cross-chain transfers throughAmarokwould take about 30 minutes and this
impacts UX.
**LiFi:** Solved by solving the related issues.
**Spearbit:** Verified.
