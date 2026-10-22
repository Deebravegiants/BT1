# [M] `create2WithStoredInitCode`

## Summary
Severity: Medium
Contest weight: 0.7661
Dataset id: 19469
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `LibStoredInitCode.sol`, the `create2WithStoredInitCode()` function, which is used to deploy contracts with the `CREATE2` opcode, is as shown:

[LibStoredInitCode.sol#L106-L117](https://github.com/code-423n4/2023-10-wildcat/blob/main/src/libraries/LibStoredInitCode.sol#L106-L117)

```solidity
function create2WithStoredInitCode(
    address initCodeStorage,
    bytes32 salt,
    uint256 value
) internal returns (address deployment) {
    assembly {
        let initCodePointer := mload(0x40)
        let initCodeSize := sub(extcodesize(initCodeStorage), 1)
        extcodecopy(initCodeStorage, initCodePointer, 1, initCodeSize)
        deployment := create2(value, initCodePointer, initCodeSize, salt)
    }
}
```

The `create2` opcode returns `address(0)` if contract deployment reverted. However, as seen from above, `create2WithStoredInitCode()` does not check if the `deployment` address is `address(0)`.

This is an issue as `deployMarket()` will not revert when deployment of the `WildcatMarket` contract fails:

[WildcatMarketController.sol#L354-L357](https://github.com/code-423n4/2023-10-wildcat/blob/main/src/WildcatMarketController.sol#L354-L357)

    LibStoredInitCode.create2WithStoredInitCode(marketInitCodeStorage, salt);

    archController.registerMarket(market);
    _controlledMarkets.add(market);

Therefore, if the origination fee is enabled for the protocol, users that call `deployMarket()` will pay the origination fee even if the market was not deployed.

Additionally, the `market` address will be registered in the `WildcatArchController` contract and added to `_controlledMarkets`. This will cause both sets to become inaccurate if deployment failed as `market` would be an address that has no code.

This also leads to more problems if a user attempts to call `deployMarket()` with the same `asset`, `namePrefix` and `symbolPrefix`. Since the `market` address has already been registered, `registerMarket()` will revert when called for a second time:

[WildcatArchController.sol#L192-L195](https://github.com/code-423n4/2023-10-wildcat/blob/main/src/WildcatArchController.sol#L192-L195)

    function registerMarket(address market) external onlyController {
        if (!_markets.add(market)) {
          revert MarketAlreadyExists();
        }

As such, if a user calls `deployMarket()` and market deployment fails, they cannot call `deployMarket()` with the same set of parameters ever again.

Note that it is possible for market deployment to fail, as seen in the constructor of `WildcatMarketBase`:

[WildcatMarketBase.sol#L79-L99](https://github.com/code-423n4/2023-10-wildcat/blob/main/src/market/WildcatMarketBase.sol#L79-L99)

    if ((parameters.protocolFeeBips > 0).and(parameters.feeRecipient == address(0))) {
      revert FeeSetWithoutRecipient();
    }
    if (parameters.annualInterestBips > BIP) {
      revert InterestRateTooHigh();
    }
    if (parameters.reserveRatioBips > BIP) {
      revert ReserveRatioBipsTooHigh();
    }
    if (parameters.protocolFeeBips > BIP) {
      revert InterestFeeTooHigh();
    }
    if (parameters.delinquencyFeeBips > BIP) {
      revert PenaltyFeeTooHigh();
    }

    // Set asset metadata
    asset = parameters.asset;
    name = string.concat(parameters.namePrefix, queryName(parameters.asset));
    symbol = string.concat(parameters.symbolPrefix, querySymbol(parameters.asset));
    decimals = IERC20Metadata(parameters.asset).decimals();

For example, the protocol could have configured `protocolFeeBips` or `feeRecipient` incorrectly. Alternatively, `asset` could be an invalid address, or an ERC20 token that does not have the `name()`, `symbol()` or `decimal()` function.

## Proof of Concept
The following test demonstrates how `deployMarket()` does not revert even if deployment of the `WildcatMarket` contract failed, and how it reverts when attempting to deploy the same market with valid parameters afterward:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity >=0.8.20;

import 'src/WildcatArchController.sol';
import 'src/WildcatMarketControllerFactory.sol';

import 'forge-std/Test.sol';
import 'test/shared/TestConstants.sol';
import 'test/helpers/MockERC20.sol';

contract MarketDeploymentRevertTest is Test {
    // Wildcat contracts
    WildcatArchController archController;
    WildcatMarketControllerFactory controllerFactory;
    WildcatMarketController controller;
    
    // Test contracts
    MockERC20 originationFeeAsset = new MockERC20();
    MockERC20 marketAsset = new MockERC20();

    // Users
    address BORROWER;

    function setUp() external {
        // Deploy Wildcat contracts
        archController = new WildcatArchController();
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
        controllerFactory = new WildcatMarketControllerFactory(
            address(archController),
            address(0),
            constraints
        );

        // Register controllerFactory in archController
        archController.registerControllerFactory(address(controllerFactory));

        // Setup borrower
        BORROWER = makeAddr("BORROWER");
        originationFeeAsset.mint(BORROWER, 10e18);
        archController.registerBorrower(BORROWER);

        // Deploy controller
        vm.prank(BORROWER);
        controller = WildcatMarketController(controllerFactory.deployController());
    }

    function test_marketDeploymentDoesntRevert() public {
        // Set protocol fee to larger than BIP
        controllerFactory.setProtocolFeeConfiguration(
            address(1),
            address(originationFeeAsset),
            5e18, // originationFeeAmount,
            1e4 + 1 // protocolFeeBips
        );

        string memory namePrefix = "Market ";
        string memory symbolPrefix = "MKT-";

        // deployMarket() does not revert
        vm.startPrank(BORROWER);
        originationFeeAsset.approve(address(controller), 5e18);
        address market = controller.deployMarket(
            address(marketAsset),
            namePrefix,
            symbolPrefix,
            type(uint128).max,
            MaximumAnnualInterestBips,
            MaximumDelinquencyFeeBips,
            MaximumWithdrawalBatchDuration,
            MaximumReserveRatioBips,
            MaximumDelinquencyGracePeriod
        );
        vm.stopPrank();

        // However, the market was never deployed and borrower paid the origination fee
        assertEq(market.code.length, 0);
        assertEq(originationFeeAsset.balanceOf(BORROWER), 5e18);

        // Set protocol fee to valid value
        controllerFactory.setProtocolFeeConfiguration(
            address(1),
            address(originationFeeAsset),
            5e18, // originationFeeAmount,
            0 // protocolFeeBips
        );

        // Call deployMarket() with valid parameters reverts as market address is already registered
        vm.startPrank(BORROWER);
        originationFeeAsset.approve(address(controller), 5e18);
        vm.expectRevert(WildcatArchController.MarketAlreadyExists.selector);
        market = controller.deployMarket(
            address(marketAsset),
            namePrefix,
            symbolPrefix,
            type(uint128).max,
            MaximumAnnualInterestBips,
            MaximumDelinquencyFeeBips,
            MaximumWithdrawalBatchDuration,
            MaximumReserveRatioBips,
            MaximumDelinquencyGracePeriod
        );
        vm.stopPrank();
    }
}
```

## Recommendation
In `create2WithStoredInitCode()`, consider checking if the `deployment` address is `address(0)`, and reverting if so:

[LibStoredInitCode.sol#L106-L117](https://github.com/code-423n4/2023-10-wildcat/blob/main/src/libraries/LibStoredInitCode.sol#L106-L117)

```solidity
function create2WithStoredInitCode(
    address initCodeStorage,
    bytes32 salt,
    uint256 value
) internal returns (address deployment) {
    assembly {
        let initCodePointer := mload(0x40)
        let initCodeSize := sub(extcodesize(initCodeStorage), 1)
        extcodecopy(initCodeStorage, initCodePointer, 1, initCodeSize)
        deployment := create2(value, initCodePointer, initCodeSize, salt)
        if iszero(deployment) {
            mstore(0x00, 0x30116425) // DeploymentFailed()
            revert(0x1c, 0x04)
        }
    }
}
```
