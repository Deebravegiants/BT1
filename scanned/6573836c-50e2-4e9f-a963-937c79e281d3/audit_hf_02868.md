# [H] TradableSideVault: accepted tokens cannot be activated, deactivated or deleted

## Summary
Severity: High
Contest weight: 0.5873
Dataset id: 16122
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation of the TradableSideVault, doesn't allow the following operations:
- aat+ - activate accepted token
- aat- - deactivate accepted token
- dat - delete accepted token
This is due to a bug in the decoding of the message payload on the sideVault. In function _nonblockingLzReceive(), the payload (which contains the messageType string and the token address) is only being decoded to an address, which will be set to the first 20 bytes of the payload, a value that has nothing to do with the token address. Since the functions to activate, deactivate and delete tokens require that the token exists, these calls will revert when called through layerZero.
Take a look at the following code:
```solidity
function test() external {
    address token = address(this); // 0x9d83e140330758a8fF…
    bytes memory payload = abi.encode("aat", token);
    (string memory messageType) = abi.decode(payload, (string)); // returns "aat"
    (address token_) = abi.decode(payload, (address)); // returns 0x0000000000000000000000000000000000000060
}
```
Here, the value for the decoded token address has nothing to do with the value that was encoded.

## Recommendation
Replace (address token_) = abi.decode(payload, (address)) with (, address token_) = abi.decode(payload, (string, address)) and test these functions.
