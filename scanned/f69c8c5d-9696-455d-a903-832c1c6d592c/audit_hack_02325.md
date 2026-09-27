# [M] \[M04\] Insufficient incentives to liquidator

## Summary
Severity: Medium
Source: https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol
Type: audit-issue

## Details
The [Holdefi contract](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol) implements the [liquidation process](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L429) for those accounts that may have an [under-collateralized balance or that may have been inactive for a whole year](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L432) without interacting with the project.

The liquidation process is a very important part of every DeFi project because it allows to extinguish the problem of having the whole system under-collateralized under critical conditions of the market, and it needs a design that incentivizes its speed of execution.

Nevertheless, the only incentive that a liquidator has when calling [the liquidateBorrowerCollateral function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L429) is to update its [last time of activity](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L447). Not only that, but also it only updates the latest activity time for the collateral type involved in the liquidation process and not all the activity times of all collaterals. Liquidators that do not have the collateral involved in the contract, or any collateral at all, will not have any benefit for calling the liquidation process.

Furthermore, given that the cost of calling [the liquidateBorrowerCollateral function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L429) will be high due to the `for` loop in [the clearDebts function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L410), as it was pointed out in the issue **“\[M02\] List of markets can endlessly grow”**, and even though buying discounted collateral assets could be considered as an incentive to the liquidators, the liquidators have a low incentive to reduce the liquidable accounts’ borrows of the platform. This is because the account liquidation process is detached from the liquidated-collateral asset purchase, making that between those function calls, a third party could front-run the transaction from the liquidator that calls [the buyLiquidatedCollateral function](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L464), by increasing the gas price, just after the transaction to the`liquidateBorrowerCollateral` function was mined. That way, the liquidator would end up paying for the expensive liquidation process, without receiving any benefit.

Consider improving the incentive design to give the liquidators higher incentives to execute the liquidation process, or merging the functionalities from the `liquidateBorrowerCollateral` and the `buyLiquidatedCollateral` functions under one.

**Update**: _Not fixed. Holdefi’s statement for this issue:_

> A 5% discount for buying collateral assets can incentivize the liquidator to liquidate collaterals and then buy it.

_We have updated our suggestion to make it clearer._
