# [M] Users can gas grief or completely block keep-

## Summary
Severity: Medium
Contest weight: 0.5936
Dataset id: 22895
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When keepers cancel users' orders, the refund gas is sent back to the user. If the user has a fallback function that specifically reverts or consumes excessive gas, the keeper's transaction can fail or exhaust its gas, causing economic harm to the keeper.

Almost every facet function uses the following pattern. For example:

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
    // @review gas sent to keeper and refund sent to user and loss is accounted if there are any
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

In the GasProcess::processExecutionFee function, if there is an excess amount to be refunded, the ether is sent to the user with infinite gas:

```solidity
function processExecutionFee(PayExecutionFeeParams memory cache) external {
    VaultProcess.withdrawEther(cache.keeper, executionFee);
    if (refundFee > 0) {
        VaultProcess.withdrawEther(cache.account, refundFee);
    }
}
```

Users can perform two malicious actions:
1. Spend all the remaining gas from the keeper's transaction, causing gas griefing and loss of funds for the keeper.
2. If this is a cancel transaction, which can only be triggered by the keeper, or any action the user does not want the keeper to succeed in, the user can set the fallback function of the contract account to revert, blocking the keeper from calling the transaction indefinitely.

Since this involves permanent blocking and loss of funds for keepers I will label this as high.

## Recommendation
There can be several fixes here but the best is probably to check if the account has code or not and send ether accordingly.
