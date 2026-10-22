# [H] Wrong precision when adding balance within

## Summary
Severity: High
Contest weight: 0.8936
Dataset id: 22940
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Wrong precision when adding balance within the restoreBridgeTransaction function, leading to loss of assets. In Line 90 below, the AccountStorage.layout().balances stores the account's balance in 18 precision, while the bridgeTransaction.amount stores the amount of token to be bridged in token native precision (e.g., USDC = 6 decimals). ocol-core/contracts/facets/Bridge/BridgeFacetImpl.sol#L90 File: BridgeFacetImpl.sol
```solidity
function restoreBridgeTransaction(uint256 transactionId, uint256 validAmount) internal {
    BridgeStorage.Layout storage bridgeLayout = BridgeStorage.layout();
    BridgeTransaction storage bridgeTransaction = bridgeLayout.bridgeTransactions[transactionId];
    require(bridgeTransaction.status == BridgeTransactionStatus.SUSPENDED, "BridgeFacet: Invalid status");
    require(bridgeLayout.invalidBridgedAmountsPool != address(0), "BridgeFacet: Zero address");
    AccountStorage.layout().balances[bridgeLayout.invalidBridgedAmountsPool] += (bridgeTransaction.amount - validAmount);
    bridgeTransaction.status = BridgeTransactionStatus.RECEIVED;
    bridgeTransaction.amount = validAmount;
}
```
Assume that the number of tokens to bridge is 10000 USDC (10000e6). Thus, bridgeTransaction.amount will be set to 10000e6. The protocol detects an anomaly with the bridging transaction and suspends it. After reviewing the transaction, the protocol decides to deduct 50% of the total bridged amount (5000 USDC). The protocol executes restoreBridgeTransaction function with validAmount parameter set to 5000 USDC (1e6). The balance of "invalidBridgedAmountsPool" account will be incremented by 5000e6, as shown below. This is incorrect because the account balance in the protocol is denominated in 18 decimal precision. Over here, the code fails to convert the native token precision to the protocol's native precision (18) before assigning it to the account balance.
```solidity
AccountStorage.layout().balances[bridgeLayout.invalidBridgedAmountsPool] += (bridgeTransaction.amount - validAmount);
AccountStorage.layout().balances[bridgeLayout.invalidBridgedAmountsPool] += 10000e6 - 5000e6
AccountStorage.layout().balances[bridgeLayout.invalidBridgedAmountsPool] += 5000e6
```
When the protocol attempts to withdraw the assets from the "invalidBridgedAmountsPool" account, the accountLayout.balances[msg.sender] will be 5000e6, and thus, the maximum value of amountWith18Decimals will be 5000e6. If amountWith18Decimals is 5000e6, the maximum amount that can be withdrawn will be 0.000000000000005 USDC based on the following formula. The protocol should have received 5000 USDC, but due to a precision error, it could only receive a maximum of 0.000000000000005 USDC, resulting in a loss of assets.
```solidity
amountWith18Decimals = (amount * 1e18) / (10 ** IERC20Metadata(appLayout.collateral).decimals());
5000e6 = (amount * 1e18) / 1e6
5000e6 / 1e6 = amount * 1e18
5000 = amount * 1e18
amount = 5000/1e18
amount = 0.000000000000005
```
ocol-core/contracts/facets/Account/AccountFacetImpl.sol#L33 File: AccountFacetImpl.sol
```solidity
function withdraw(address user, uint256 amount) internal {
    AccountStorage.Layout storage accountLayout = AccountStorage.layout();
    GlobalAppStorage.Layout storage appLayout = GlobalAppStorage.layout();
    require(
        block.timestamp >= accountLayout.withdrawCooldown[msg.sender] + MAStorage.layout().deallocateCooldown,
        "AccountFacet: Cooldown hasn't reached"
    );
    uint256 amountWith18Decimals = (amount * 1e18) / (10 ** IERC20Metadata(appLayout.collateral).decimals());
    accountLayout.balances[msg.sender] -= amountWith18Decimals;
    IERC20(appLayout.collateral).safeTransfer(user, amount);
}
```
Loss of assets due to precision error, as shown in the above scenario.

## Recommendation
Scale up to the protocol's native precision of 18 decimals before assigning it to the account balance.
```solidity
AccountStorage.layout().balances[bridgeLayout.invalidBridgedAmountsPool] += ((bridgeTransaction.amount - validAmount) * 1e18) / (10 ** IERC20Metadata(appLayout.collateral).decimals());
```
