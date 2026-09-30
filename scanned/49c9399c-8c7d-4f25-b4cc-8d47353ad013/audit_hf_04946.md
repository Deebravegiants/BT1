# [M] Missing compensation for the 21,000 intrin-

## Summary
Severity: Medium
Contest weight: 0.4345
Dataset id: 22899
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Every EVM transaction (on both L1 and L2) has an immediate 21,000 intrinsic gas cost, it's charged before any execution of smart contract code. The current implementation is missing to compensate this portion of gas cost, the keeper would suffer lost on each transaction.

Reference: https://stackoverflow.com/questions/50827894/why-does-my-ethereum-transaction-cost-21000-more-gas-than-i-expect

The current startGas (L67) can't account for the 21,000 intrinsic gas cost.

File: contracts\facets\OrderFacet.sol

```solidity
function executeOrder(uint256 orderId, OracleProcess.OracleParam[] calldata oracles) external override {
    uint256 startGas = gasleft();
    RoleAccessControl.checkRole(RoleAccessControl.ROLE_KEEPER);
    Order.OrderInfo memory order = Order.get(orderId);
    if (order.account == address(0)) {
    }
    OracleProcess.setOraclePrice(oracles);
    OrderProcess.executeOrder(orderId, order);
    OracleProcess.clearOraclePrice();
    GasProcess.processExecutionFee(
        GasProcess.PayExecutionFeeParams(
            order.isExecutionFeeFromTradeVault
                ? IVault(address(this)).getTradeVaultAddress()
                : IVault(address(this)).getPortfolioVaultAddress(),
            order.executionFee,
            startGas,
            msg.sender,
            order.account
        )
    );
}
```

The keeper will suffer continuing 21,000 intrinsic gas losses on each transaction

## Recommendation
File: contracts\facets\OrderFacet.sol
66:
function executeOrder(uint256 orderId, OracleProcess.OracleParam[] calldata oracles) external override {
-67:
uint256 startGas = gasleft();
+67:
plus 9000 extra gas for calldata and facet lookup in diamond fallback() function
