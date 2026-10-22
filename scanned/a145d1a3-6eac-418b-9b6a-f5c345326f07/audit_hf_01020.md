# [H] Improper native token handling in matchBid and fulfillOrder causes transaction failures

## Summary
Severity: High
Contest weight: 0.8854
Dataset id: 3763
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The matchBid function in ColonyBidRouter.sol fails when the considerationToken specified in the order parameter is a native token (e.g., ETH). This occurs because the function attempts to interact with the IERC20 interface regardless of whether the token is native or ERC20-compliant:
```solidity
IERC20 considerationToken = IERC20(order.considerationToken);
considerationToken.approve(SEAPORT, bid.bidAmount);
ISeaport(SEAPORT).fulfillBasicOrder{value: msg.value}(order);
```
For native tokens, both the transferFrom and approve calls will fail because they are not applicable to ETH. This will result in a transaction revert whenever ETH is used as the considerationToken. Moreover, the fulfillOrder function in the SeaportProxy contract does not account for cases where the consideration token is the native token (e.g., ETH). This results in a failure when attempting to process such orders. The function uses the following logic to handle the consideration token:
```solidity
IERC20 considerationToken = IERC20(order.considerationToken);
considerationToken.approve(SEAPORT, totalConsiderationAmount);
ISeaport(SEAPORT).fulfillBasicOrder{value: msg.value}(order);
```
This implementation assumes the consideration token is an ERC20 token and attempts to call transferFrom and approve methods on it. However, if the considerationToken is the native token (e.g., ETH), these calls will fail because native tokens do not support the ERC20 interface. The issue leads to failed transactions whenever users attempt to fulfill an order with a native token as the consideration. This significantly limits the functionality of the fulfillOrder function and impacts usability.

## Recommendation
```solidity
// Native token handling
if (msg.value < bid.bidAmount) {
    revert InsufficientEthSent();
}
ISeaport(SEAPORT).fulfillBasicOrder{value: bid.bidAmount}(order);
} else {
    // ERC20 token handling
    IERC20 considerationToken = IERC20(order.considerationToken);
    considerationToken.approve(SEAPORT, bid.bidAmount);
    ISeaport(SEAPORT).fulfillBasicOrder(order);
```
