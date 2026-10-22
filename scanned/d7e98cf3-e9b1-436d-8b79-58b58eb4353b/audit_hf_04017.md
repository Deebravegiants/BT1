# [M] Possible incorrect price for tokens in Balancer

## Summary
Severity: Medium
Contest weight: 0.5903
Dataset id: 20427
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Incorrect price calculation of tokens in StablePools if amplification factor is being updated The amplification parameter used to calculate the invariant can be in a state of update. In such a case, the current amplification parameter can differ from the amplificaiton parameter at the time of the last invariant calculation. The current implementaiton of getTokenPriceFromStablePool doesn't consider this and always uses the amplification factor obtained by calling getLastInvariant
```solidity
ules/PRICE/submodules/feeds/BalancerPoolTokenPrice.sol#L811-L827
function getTokenPriceFromStablePool(
    address lookupToken_,
    uint8 outputDecimals_,
    bytes calldata params_
) external view returns (uint256) {
    .....
    try pool.getLastInvariant() returns (uint256, uint256 ampFactor) {
        lookupTokensPerDestinationToken = StableMath._calcOutGivenIn(
            ampFactor,
            balances_,
            destinationTokenIndex,
            lookupTokenIndex,
            1e18,
            StableMath._calculateInvariant(ampFactor, balances_) // Sometimes the fetched invariant value does not work, so calculate it
        );
```
https://vscode.blockscan.com/ethereum/0x1e19cf2d73a72ef1332c882f20534b6519be0276 StablePool.sol
```solidity
function startAmplificationParameterUpdate(uint256 rawEndValue, uint256 endTime) external authenticate {
    obtained by calling _getAmplificationParameter()
function _onSwapGivenIn(
    SwapRequest memory swapRequest,
    uint256[] memory balances,
    uint256 indexIn,
    uint256 indexOut
) internal virtual override whenNotPaused returns (uint256) {
    (uint256 currentAmp, ) = _getAmplificationParameter();
    uint256 amountOut = StableMath._calcOutGivenIn(currentAmp, balances, indexIn, indexOut, swapRequest.amount);
    return amountOut;
}
```
In case the amplification parameter of a pool is being updated by the admin, wrong price will be calculated.

## Recommendation
Use the latest amplification factor by callling the getAmplificationParameter function
