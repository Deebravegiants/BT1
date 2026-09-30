# [M] Napier pool owner can unfairly increase pro-

## Summary
Severity: Medium
Contest weight: 0.4782
Dataset id: 22481
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently there is no limit to how often a poolOwner can update fees which can be abused to earn more fees by charging users higher swap fees than they expect. The NapierPool::setFeeParameter function allows the poolOwner to set the protocolFeePercent at any point to a maximum value of 100%. The poolOwner is a trusted party but should not be able to abuse protocol settings to earn more revenue. There are no limits to how often this can be updated. A malicious poolOwner could change the protocol swap fees unfairly for users by front-running swaps and increasing fees to higher values on unsuspecting users. An example scenario is: • The poolOwner sets swap fees to 1% to attract users • The poolOwner front runs all swaps and changes the swap fees to the maximum value of 100% • After the swap the poolOwner resets protocolFeePercent to a low value to attract more users

## Proof of Concept
```solidity
function test_protocol_owner_frontRuns_swaps_with_higher_fees() public whenMaturityNotPassed {
    // pre-condition
    vm.warp(maturity - 30 days);
    deal(address(pts[0]), alice, type(uint96).max, false); // ensure alice has enough pt

    uint256 preBaseLptSupply = tricrypto.totalSupply();
    uint256 ptInDesired = 100 * ONE_UNDERLYING;
    uint256 expectedBaseLptIssued = tricrypto.calc_token_amount([ptInDesired, 0, 0], true);

    // Pool owner sees swap about to occur and front runs updating fees to max value

    vm.startPrank(owner);
    pool.setFeeParameter("protocolFeePercent", 100);
    vm.stopPrank();
    // execute
    vm.prank(alice);
    uint256 underlyingOut = pool.swapPtForUnderlying(
        0, ptInDesired, recipient,
        abi.encode(CallbackInputType.SwapPtForUnderlying, SwapInput(underlying, pts[0]))
    );

    // sanity check
    uint256 protocolFee = SwapEventsLib.getProtocolFeeFromLastSwapEvent(pool);
    assertGt(protocolFee, 0, "fee should be charged");
}
```

## Recommendation
Introduce a delay in fee updates to ensure users receive the fees they expect.
