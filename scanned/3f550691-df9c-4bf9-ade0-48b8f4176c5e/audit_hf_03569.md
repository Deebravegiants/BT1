# [M] `collectFees

## Summary
Severity: Medium
Contest weight: 0.8268
Dataset id: 19468
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `collectFees()` function calls `_writeState()` before transferring assets to the `feeRecipient`:

[WildcatMarket.sol#L106-L107](https://github.com/code-423n4/2023-10-wildcat/blob/main/src/market/WildcatMarket.sol#L106-L107)

```solidity
_writeState(state);
asset.safeTransfer(feeRecipient, withdrawableFees);
```

However, `_writeState()` calls `totalAssets()` when checking if the market is delinquent:

[WildcatMarketBase.sol#L448-L453](https://github.com/code-423n4/2023-10-wildcat/blob/main/src/market/WildcatMarketBase.sol#L448-L453)

```solidity
function _writeState(MarketState memory state) internal {
  bool isDelinquent = state.liquidityRequired() > totalAssets();
  state.isDelinquent = isDelinquent;
  _state = state;
  emit StateUpdated(state.scaleFactor, isDelinquent);
}
```

`totalAssets()` returns the current asset balance of the market:

[WildcatMarketBase.sol#L238-L240](https://github.com/code-423n4/2023-10-wildcat/blob/main/src/market/WildcatMarketBase.sol#L238-L240)

```solidity
function totalAssets() public view returns (uint256) {
  return IERC20(asset).balanceOf(address(this));
}
```

Since the transfer of assets is only performed _after_ `_writeState()` is called, `totalAssets()` will be higher than it should be in `_writeState()`. This could cause `collectFees()` to incorrectly update `state.isDelinquent` to `false` when the market is still delinquent.

For example:

  * Assume a market has the following state:

    * `liquidityRequired() = 1050`.
    * `totalAssets() = 1000`.
    * `state.accruedProtocolFees = 50`.
  * The market’s borrower calls `collectFees()`. In `_writeState()`:

    * `liquidityRequired() = 1050 - 50 = 1000`.
    * `totalAssets() = 1000` since the transfer of assets has not occurred.
    * As `liquidityRequired() == totalAssets()`, `isDelinquent` is updated to `false`.
    * However, the market is actually still delinquent as `totalAssets()` will be `950` after the call to `collectFees()`.

## Proof of Concept
The following test demonstrates how `collectFees()` incorrectly updates `state.isDelinquent` to `false` when the market is still delinquent:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity >=0.8.20;

import 'src/WildcatArchController.sol';
import 'src/WildcatMarketControllerFactory.sol';

import 'forge-std/Test.sol';
import 'test/shared/TestConstants.sol';
import 'test/helpers/MockERC20.sol';

contract CollectFeesTest is Test {
    // Wildcat contracts
    WildcatMarketController controller;
    WildcatMarket market;
    
    // Test contracts
    MockERC20 asset = new MockERC20();

    // Users
    address AIKEN;
    address DUEET;

    function setUp() external {
        // Deploy Wildcat contracts
        WildcatArchController archController = new WildcatArchController();
        MarketParameterConstraints memory constraints = MarketParameterConstraints({
            minimumDelinquencyGracePeriod: MinimumDelinquencyGracePeriod,
            maximumDelinquencyGracePeriod: MaximumDelinquencyGracePeriod,
            minimumReserveRatioBips: MinimumReserveRatioBips,
            maximumReserveRatioBips: MaximumReserveRatioBips,
            minimumDelinquencyFeeBips: MinimumDelinquencyFeeBips,
            maximumDelinquencyFeeBips: MaximumDelinquencyFeeBips,
            minimumWithdrawalBatchDuration: MinimumWithdrawalBatchDuration,
            maximumWithdrawalBatchDuration: MaximumWithdrawalBatchDuration,
            minimumAnnualInterestBips: MinimumAnnualInterestBips,
            maximumAnnualInterestBips: MaximumAnnualInterestBips
        });
        WildcatMarketControllerFactory controllerFactory = new WildcatMarketControllerFactory(
            address(archController),
            address(0),
            constraints
        );

        // Set protocol fee to 10%
        controllerFactory.setProtocolFeeConfiguration(
            address(1),
            address(0),
            0, 
            1000 // protocolFeeBips
        );

        // Register controllerFactory in archController
        archController.registerControllerFactory(address(controllerFactory));

        // Setup Aiken and register him as borrower
        AIKEN = makeAddr("AIKEN");
        archController.registerBorrower(AIKEN);
        asset.mint(AIKEN, 1000e18);

        // Setup Dueet and give him some asset token
        DUEET = makeAddr("DUEET");
        asset.mint(DUEET, 1000e18);
        
        // Deploy controller and market for Aiken
        vm.prank(AIKEN);
        (address _controller, address _market) = controllerFactory.deployControllerAndMarket(
            "Market Token",
            "MKT",
            address(asset),
            type(uint128).max,
            MaximumAnnualInterestBips,
            MaximumDelinquencyFeeBips,
            MaximumWithdrawalBatchDuration,
            MaximumReserveRatioBips,
            MaximumDelinquencyGracePeriod
        );
        controller = WildcatMarketController(_controller);
        market = WildcatMarket(_market);
    }

    function test_collectFeesUpdatesDelinquencyWrongly() public {
        // Register Dueet as lender
        address[] memory arr = new address[](1);
        arr[0] = DUEET;
        vm.prank(AIKEN);
        controller.authorizeLenders(arr);

        // Dueet becomes a lender in the market
        vm.startPrank(DUEET);
        asset.approve(address(market), 1000e18);
        market.depositUpTo(1000e18);
        vm.stopPrank();

        // Some time passes, market becomes delinquent
        skip(2 weeks);
        market.updateState();
        MarketState memory state = market.previousState();
        assertTrue(state.isDelinquent);

        // Aiken tops up some assets
        uint256 amount = market.coverageLiquidity() -  market.totalAssets() - market.accruedProtocolFees();
        vm.prank(AIKEN);
        asset.transfer(address(market), amount);
        
        // Someone calls collectFees()
        market.collectFees();

        // Market was updated to not delinquent
        state = market.previousState();
        assertFalse(state.isDelinquent);

        // However, it should be delinquent as liquidityRequired > totalAssets()
        assertGt(market.coverageLiquidity(), market.totalAssets());
    }
}
```

## Recommendation
In `collectFees()`, consider calling `_writeState()` after assets have been transferred to the `feeRecipient`:

[WildcatMarket.sol#L106-L107](https://github.com/code-423n4/2023-10-wildcat/blob/main/src/market/WildcatMarket.sol#L106-L107)

```solidity
// _writeState(state);
asset.safeTransfer(feeRecipient, withdrawableFees);
_writeState(state);
```

Mitigated [here](https://github.com/wildcat-finance/wildcat-protocol/commit/016f6f2d43fa33cebe15c422f8663c76a4e4fd10).

Note: For full discussion, see[here](https://github.com/code-423n4/2023-10-wildcat-findings/issues/500).
