# [H] Missing transferable Check in send

## Summary
Severity: High
Contest weight: 0.8631
Dataset id: 7556
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Token.sol contract is designed to prevent token transfers unless transfersEnabled is true or msg.sender is the controller. This restriction is enforced through the transferable modifier:
```solidity
modifier transferable() {
    require(msg.sender == controller || transfersEnabled, "NON_TRANSFERABLE");
}
```
However, the send function does not apply this modifier, allowing token transfers even when transfersEnabled is false:
```solidity
_transfer(msg.sender, to, value); // @audit-issue: No transferable check, bypassing transfer restriction
emit Sent(msg.sender, msg.sender, to, value, data, "");
if (isContract(to))
    IERC777Recipient(to).tokensReceived(msg.sender, msg.sender, to, value, data, "");
```
This oversight allows anyone to transfer tokens even when transfers are explicitly disabled, breaking the intended invariant of the contract.

## Recommendation
Add the transferable modifier to the send function to ensure transfer restrictions are enforced:
```solidity
_transfer(msg.sender, to, value);
emit Sent(msg.sender, msg.sender, to, value, data, "");
if (isContract(to))
    IERC777Recipient(to).tokensReceived(msg.sender, msg.sender, to, value, data, "");
```
This change ensures that only the controller or users sending tokens when transfersEnabled is true can execute transfers, maintaining the intended access control.
