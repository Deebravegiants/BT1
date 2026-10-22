# [H] Pumps are not updated in the shift

## Summary
Severity: High
Contest weight: 0.8439
Dataset id: 18930
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `Well` contract mandates that the `Pumps` should be updated with the previous block’s `reserves` in case `reserves` are changed in the current block to reflect the price change accurately.

However, this doesn’t happen in the `shift()` and `sync()` functions, providing an opportunity for any user to manipulate the `reserves` in the current block before updating the `Pumps` with new manipulated `reserves` values.

## Proof of Concept
1. A malicious user performs a `shift()` operation to update `reserve`s to desired amounts in the current block, thereby overriding the `reserves` from the previous block.
2. The user performs `swapFrom()/swapTo()` operations to extract back the funds used in the `shift()` function. As a result, the attacker is not affected by any arbitration as pool `reserves` revert back to the original state.
3. The `swapFrom()/swapTo()` operations trigger the `Pumps` update with invalid `reserves`, resulting in oracle manipulation.

Note: The `sync()` function can also manipulate `reserves` in the current block, but it’s less useful than `shift()` from an attacker’s perspective.

This test illustrates how to use `shift()` to manipulate `Pumps` data.

Create `test/pumps/Pump.Manipulation.t.sol` and run `forge test --match-test manipulatePump`.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import {TestHelper, Call} from "../TestHelper.sol";
import {MultiFlowPump} from "src/pumps/MultiFlowPump.sol";
import {from18} from "test/pumps/PumpHelpers.sol";

contract PumpManipulationTest is TestHelper {
    MultiFlowPump pump;

    function setUp() public {
        pump = new MultiFlowPump(
            from18(0.5e18), // cap reserves if changed +/- 50% per block
            from18(0.5e18), // cap reserves if changed +/- 50% per block
            12, // block time
            from18(0.9e18) // ema alpha
        );

        Call[] memory _pumps = new Call[](1);
        _pumps[0].target = address(pump);
        _pumps[0].data = new bytes(0);

        setupWell(2,_pumps);
    }

    function test_manipulatePump() public prank(user) {
        uint256 amountIn = 1 * 1e18;

        // 1. equal swaps, reserves should be unchanged
        uint256 amountOut = well.swapFrom(tokens[0], tokens[1], amountIn, 0, user, type(uint256).max);
        well.swapFrom(tokens[1], tokens[0], amountOut, 0, user, type(uint256).max);

        uint256[] memory lastReserves = pump.readLastReserves(address(well));
        assertApproxEqAbs(lastReserves[0], 1000 * 1e18, 1);
        assertApproxEqAbs(lastReserves[1], 1000 * 1e18, 1);

        // 2. equal shift + swap, reserves should be unchanged (but are different)
        increaseTime(120);
        
        tokens[0].transfer(address(well), amountIn);
        amountOut = well.shift(tokens[1], 0, user);
        well.swapFrom(tokens[1], tokens[0], amountOut, 0, user, type(uint256).max);

        lastReserves = pump.readLastReserves(address(well));
        assertApproxEqAbs(lastReserves[0], 1000 * 1e18, 1);
        assertApproxEqAbs(lastReserves[1], 1000 * 1e18, 1);
    }
}
```

## Recommendation
Update `Pumps` in the `shift()` and `sync()` function.

```solidity
    function shift(
        IERC20 tokenOut,
        uint256 minAmountOut,
        address recipient
    ) external nonReentrant returns (uint256 amountOut) {
        IERC20[] memory _tokens = tokens();
        uint256[] memory reserves = _updatePumps(_tokens.length);
    
    function sync() external nonReentrant {
        IERC20[] memory _tokens = tokens();
        uint256[] memory reserves = _updatePumps(_tokens.length);
```

This issue has been fixed by updating the Pumps in `shift(...)` and `sync(...)`:
 
  * <https://github.com/BeanstalkFarms/Basin/blob/91233a22005986aa7c9f3b0c67393842cd8a8e4d/src/Well.sol#L380>
  * <https://github.com/BeanstalkFarms/Basin/blob/91233a22005986aa7c9f3b0c67393842cd8a8e4d/src/Well.sol#L628>
