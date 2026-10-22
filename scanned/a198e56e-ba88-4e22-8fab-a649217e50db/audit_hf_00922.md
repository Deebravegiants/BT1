# [M] Potential loss of LP Fees

## Summary
Severity: Medium
Contest weight: 0.5938
Dataset id: 2767
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a token sale completes, the corresponding curvePool is set to paused. Subsequently, the owner can invoke TokenFactory::moveToAMM to create a pool on Uniswap and add liquidity (TokenFactory#L888-905). This action mints a Uniswap position NFT and stores its ID (TokenFactory#L858) for fee collection later. However, Uniswap may return ETH if the full amount isn't used for liquidity, which can incorrectly leave the curve's ETH balance non-zero (curve.ethBalance) (TokenFactory#L917-931):
```solidity
function _createPoolAndAddLiquidity(
    address erc20Address,
    uint256 ethBalance,
    uint256 tokenBalance,
    uint16 slippageBips
) internal returns (uint256 tokenId) {
    // Remove ERC20 allowance and update ETH balance (if refunded)
    if (amount0Added < amount0) {
        if (token0 == WETH9) {
            curve.ethBalance = amount0 - amount0Added;
        } else {
            TransferHelper.safeApprove(token0, address(UNISWAP_V3_POSITION_MANAGER), 0);
        }
    }
    if (amount1Added < amount1) {
        if (token1 == WETH9) {
            curve.ethBalance = amount1 - amount1Added;
        } else {
            TransferHelper.safeApprove(token1, address(UNISWAP_V3_POSITION_MANAGER), 0);
        }
    }
}
```
This non-zero balance can erroneously allow TokenFactory::moveToAMM to be called again since the function checks if there's enough liquidity to proceed without reverting (TokenFactory#L854-856):
```solidity
function moveToAMM(address erc20Address, uint16 slippageBips)
    external
    onlyOwner
    nonReentrant
    validToken(erc20Address)
{
    if (!curves[erc20Address].isPaused) {
        revert TokenFactory_BondingCurveNotPaused();
    }
    BondingCurveData storage curve = curves[erc20Address];
    uint256 ethBalance = curve.ethBalance;
    uint256 tokenBalance = IERC20(erc20Address).balanceOf(address(this));
    if (ethBalance == 0 || tokenBalance == 0) {
        revert TokenFactory_InsufficientLiquidity();
    }
    tokenIds[erc20Address] = _createPoolAndAddLiquidity(erc20Address, ethBalance, tokenBalance, slippageBips);
}
```
Consider the following scenario:
1. The token pool completes, and the owner initially calls moveToAMM.
2. A Uniswap pool is created, and a position is minted, but some ETH is refunded, leaving curve.ethBalance non-zero TokenFactory#L919.
3. The owner inadvertently calls moveToAMM again, perhaps triggered by an automatic script or misunderstanding in the off-chain process. An attacker could exploit this by sending tokens to meet the liquidity check (TokenFactory#L854-856), allowing the creation of another position. This new position ID overwrites the old one (TokenFactory#L858), losing the ability to claim LP fees from the initially created position in step 1. Ultimately, the contract will only be able to claim LP fees from the position created in step 3, as this position is the only one stored in tokenIds[erc20Address]. The position created in step 2 will no longer be able to claim its LP fees.

## Recommendation
To mitigate this issue, it is recommended to handle ETH refunds in a way that prevents them from being reused for another moveToAMM call.
