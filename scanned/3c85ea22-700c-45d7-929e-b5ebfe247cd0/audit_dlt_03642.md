# [M] Some functions don't check if liquidity > 0 before calling decreaseLiquidity

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-25
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/47
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L654-L658


# Vulnerability details

## Impact
- Users cannot just collect UniswapV3 fees alone.
- Users cannot call `leverageDown` with fee alone.

## Proof of concept
One of the most important features of Revert Lend is that it allows user to take loans using UniswapV3 positions as collateral while at the same time able to manage their positions; this includes collecting fees, decrease liquidity, increase liquidity,... as documented [here](https://docs.revert.finance/revert/technical-docs/auto-compounder/manage-positions)

However, the current implementation will not allow user to just collect fees. `V3Vault` contains a function called `decreaseLiquidityAndCollect`:
```solidity
function decreaseLiquidityAndCollect(DecreaseLiquidityAndCollectParams calldata params)
        external
        override
        returns (uint256 amount0, uint256 amount1)
    {
     ...
     (amount0, amount1) = nonfungiblePositionManager.decreaseLiquidity(
            INonfungiblePositionManager.DecreaseLiquidityParams(
                params.tokenId, params.liquidity, params.amount0Min, params.amount1Min, params.deadline
            )
        );
     ...
    }
```
However as you can see in the above code, the function will call `decreaseLiquidity` without checking if `liquidity` to be removed >0; if `liquidity = 0`, then `decreaseLiquidity` will revert. Below is the UniswapV3 NonfungibleTokenManager code for this situation https://github.com/Uniswap/v3-periphery/blob/main/contracts/NonfungiblePositionManager.sol#L265:

```solidity
 function decreaseLiquidity(DecreaseLiquidityParams calldata params)
        external
        payable
        override
        isAuthorizedForToken(params.tokenId)
        checkDeadline(params.deadline)
        returns (uint256 amount0, uint256 amount1)
    {
        require(params.liquidity > 0);
}
```

Using `V3Utils` transformation will not allow users to just collect fees either. The function `V3Utils.execute` does check if `liquidity >0` and collect fees:
```solidity
function execute(uint256 tokenId, Instructions memory instructions) public returns (uint256 newTokenId) {
        _validateCaller(nonfungiblePositionManager, tokenId);

        (,, address token0, address token1,,,, uint128 liquidity,,,,) = nonfungiblePositionManager.positions(tokenId);

        uint256 amount0;
        uint256 amount1;
        if (instructions.liquidity != 0) {
            (amount0, amount1) = _decreaseLiquidity(
                tokenId,
                instructions.liquidity,
                instructions.deadline,
                instructions.amountRemoveMin0,
                instructions.amountRemoveMin1
            );
        }
        (amount0, amount1) = _collectFees(
            tokenId,
            IERC20(token0),
            IERC20(token1),
            instructions.feeAmount0 == type(uint128).max
                ? type(uint128).max
                : (amount0 + instructions.feeAmount0).toUint128(),
            instructions.feeAmount1 == type(uint128).max
                ? type(uint128).max
                : (amount1 + instructions.feeAmount1).toUint128()
        );
}
```
However, after this `V3Utils` only supports 3 modes and each of these forces users to do something else beside collecting fees:
- `CHANGE_RANGE` mode forces users to mint a new UniswapV3 position
- `WITHDRAW_AND_COLLECT_AND_SWAP` forces users to swap tokens
- `COMPOUND_FEES` forces users to use all collected fee to increase liquidity

In summary, `V3Vault` and `V3Utils` won't let users collect their positions fees alone - an important feature in Revert Lend system.


One more part this is not checked is in function `LeverageTransformer.leverageDown`:
```solidity
function leverageDown(LeverageDownParams calldata params) external {
...
INonfungiblePositionManager.DecreaseLiquidityParams memory decreaseLiquidityParams = INonfungiblePositionManager
            .DecreaseLiquidityParams(
            params.tokenId, params.liquidity, params.amountRemoveMin0, params.amountRemoveMin1, params.deadline
        );
        (amount0, amount1) = nonfungiblePositionManager.decreaseLiquidity(decreaseLiquidityParams);
...
}
```
If a user pass in `LeverageDownParams.liquidity = 0`, that means they just want to use UniswapV3 collect fees to repay their debt in `V3Vault`, yet in this situation they are forced to decrease their position.


Below is a POC for this issue, save this test case to file `V3Oracle.t.my.sol` and run it using command:
`forge test --match-path test/integration/V3Vault.t.sol --match-test testCannotCollect -vvvv`

```solidity
function testCannotCollect() external {
        uint256 minLoanSize = 1000000;

        vault.setLimits(1000000, 15000000, 15000000, 15000000, 15000000);

        // lend 10 USDC
        _deposit(10000000, WHALE_ACCOUNT);

        // add collateral
        vm.startPrank(TEST_NFT_ACCOUNT);
        NPM.approve(address(vault), TEST_NFT);

        vault.create(TEST_NFT, TEST_NFT_ACCOUNT);
        // Borrow
        vault.borrow(TEST_NFT, minLoanSize);

        // Cannot just collect by setting decrease liquidity = 0
        IVault.DecreaseLiquidityAndCollectParams memory params = IVault.DecreaseLiquidityAndCollectParams(
            TEST_NFT,
            0, // liquidity to remove
            0,
            0,
            type(uint128).max,
            type(uint128).max,
            block.timestamp,
            TEST_NFT_ACCOUNT
        );
        vm.expectRevert();
        vault.decreaseLiquidityAndCollect(params);

        // Users are forced to remove some liquidity
        params = IVault.DecreaseLiquidityAndCollectParams(
            TEST_NFT,
            1, // liquidity to remove
            0,
            0,
            type(uint128).max,
            type(uint128).max,
            block.timestamp,
            TEST_NFT_ACCOUNT
        );
        vault.decreaseLiquidityAndCollect(params);

        vm.stopPrank();



    }
```

## Tool used
Manual Review

## Recommended mitigation
In function `V3Vault.decreaseLiquidityAndCollect`, the code should check if `liquidity > 0`, if not, `decreaseLiquidity` should not be called. This allow the user to collect fees.










## Assessed type

Invalid Validation
