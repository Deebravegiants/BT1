# [M] \[M01\] Sponsors can delay liquidations

## Summary
Severity: Medium
Source: https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/financial-templates/implementation/PricelessPositionManager.sol#L165
Type: audit-issue

## Details
Any under-collateralized sponsor can delay liquidation attempts by [transferring their position](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/financial-templates/implementation/PricelessPositionManager.sol#L165) to another address that they control before the [liquidation transaction targeted at the old address](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/financial-templates/implementation/Liquidatable.sol#L188) is processed. This would cause the liquidation to fail.

In most cases, sponsors that recognize that are about to be liquidated would [redeem their position](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/financial-templates/implementation/PricelessPositionManager.sol#L336). However, were sponsors able to successfully delay liquidation for long enough, they could keep the [global collateralization ratio](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/financial-templates/implementation/PricelessPositionManager.sol#L621-L624) artificially depressed, potentially below the [collateralization requirement](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/financial-templates/implementation/Liquidatable.sol#L90). In this scenario, sponsors would be able to [create under-collateralized positions](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/financial-templates/implementation/PricelessPositionManager.sol#L303) or [withdraw excessive collateral](https://github.com/UMAprotocol/protocol/blob/e6eaa48124ae3f209fb117cf05eb18292cf26d21/core/contracts/financial-templates/implementation/PricelessPositionManager.sol#L201). In the extreme case, sponsors could delay liquidation until they were insolvent.

Consider delaying position transfers for a short time window, thereby treating them similar to slow withdrawals.

**Update:** _Fixed in [PR#1314](https://github.com/UMAprotocol/protocol/pull/1314). Transfers of positions are now delayed for the same duration as slow withdrawal requests._
