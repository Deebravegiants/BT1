# [M] Liquidators can prevent users from making

## Summary
Severity: Medium
Contest weight: 0.5945
Dataset id: 20073
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Perennial protocol has a paused state in which all operations are paused. The protocol can be unpaused by privileged accounts. But when this unpause happens the liquidators can frontrun and liquidate user positions before those users get a chance to make their positions healthy.

perennial-mono/packages/perennial/contracts/collateral/Collateral.sol#L108-L135
The pauser address can pause the perennial protocol using the Controller.updatePaused function. Once the protocol is paused all these operations cannot be done by users:
• Open/close/modify current make or take positions on a product.
• Deposit or withdraw collateral.
• Liquidate under-collateralized positions.

Though, real prices from oracles will surely move up or down during this paused period. If the oracle prices go down, the users won't be allowed to add more collateral to their positions or close their positions. Hence their positions will get under-collateralized (based upon real prices).

Once the protocol is unpaused the liquidators can front-run most users and liquidate their positions. Most users will not get a chance to make their position healthy.

This results in loss of funds for the users.

Perennial also has the concept of settlement delay. Any position opened/closed at oracle version n is settled at oracle version n + 1. This also alleviates the frontrunning liquidation issue. While validating an account's health before liquidation, the protocol only considers the current maintenance requirement for the account (not the next). This makes users more prone to getting front-runned and liquidated.

By front-running any collateral deposit or position closure of a legitimate user which became under-collateralized during the paused state, the liquidator can unfairly liquidate user positions and collect liquidation profit as soon as the protocol is unpaused. This causes loss of funds to the user.

```solidity
Collateral
external
nonReentrant
notPaused
notZeroAddress(account)
isProduct(product)
collateralInvariant(account, product)
{
    _products[product].creditAccount(account, amount);
    token.pull(msg.sender, amount);
    emit Deposit(account, product, amount);
}
```

```solidity
Product
public
nonReentrant
notPaused
onlyAccountOrMultiInvoker(account)
settleForAccount(account)
closeInvariant(account)
liquidationInvariant(account)
{
    _closeTake(account, amount);
}
```

```solidity
public
nonReentrant
notPaused
onlyAccountOrMultiInvoker(account)
settleForAccount(account)
takerInvariant
closeInvariant(account)
liquidationInvariant(account)
{
    _closeMake(account, amount);
}
```

## Recommendation
Consider adding a grace period after unpausing during which liquidation remains blocked to allow users to avoid unfair liquidation by closing their positions or supplying additional collateral.
