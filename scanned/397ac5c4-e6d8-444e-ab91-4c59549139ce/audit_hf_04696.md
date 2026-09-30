# [M] UniswapV3RouterUpgradeable.sol is vulnerable

## Summary
Severity: Medium
Contest weight: 0.5943
Dataset id: 22466
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
UniswapV3RouterUpgradeable.sol never verifies that the callback msg.sender is actually a deployed pool. This allows for a provable address collision that can be used to drain all allowances to the router. Before going in details, This issue is referenced from this issue which was also mention this particular reference for similar issues. The pool address check in the callback function isn't strict enough and can suffer issues with collision. Due to the truncated nature of the create2 opcode the collision resistance is already impaired to 2^160 as that is total number of possible hashes after truncation. Obviously if you are searching for a single hash, this is (basically) impossible. The issue here is that one does not need to search for a single address as the router never verifies that the pool actually exists. This is the crux of the problem. For more details, refer this article on The probability of a hash collision. Also refer this issue.
```solidity
function uniswapV3SwapCallback(
    int256 amount0Delta,
    int256 amount1Delta,
    bytes calldata _data
) external override {
    require(amount0Delta > 0 || amount1Delta > 0);
    SwapCallbackData memory data = abi.decode(_data, (SwapCallbackData));
    (address tokenIn, address tokenOut, address payer) = verifyCallback(data);
    // . . . some code
}
```
```solidity
function verifyCallback(
    SwapCallbackData memory data
) internal view returns (address tokenIn, address tokenOut, address payer) {
    (tokenIn, tokenOut, payer) = (data.tokenIn, data.tokenOut, data.payer);
    address poolAddress = computePoolAddress(tokenIn, tokenOut, data.fee);
    require(msg.sender == poolAddress);
    // computed pool address
}
```
The verifyCallback() used in uniswapV3SwapCallback() function is used to verify that msg.sender is the address of the pool and only a require check is performed to verify if msg.sender has been computed via computePoolAddress(). According to the UniswapV3 Doc, when using uniswapV3SwapCallback, the caller of this method must be verified to be a UniswapV3Pool deployed by the canonical UniswapV3Factory. However, the function never checks with the factory that the pool exists or any of the inputs are valid in any way. tokenIn can be constant and we can achieve the variation in the hash by changing tokenOut. The attacker could use tokenIn = WETH and vary tokenOut. This would allow them to steal all allowances of WETH. Since allowances are forever until revoked, this could put hundreds of millions of dollars at risk. The pool address check in the callback function isn't strict enough and can suffer issues with collision. Address collision can cause all allowances to be drained. Although this would require a large amount of compute it is already possible to break with current computing. Given the enormity of the value potentially at stake it would be a lucrative attack to anyone who could fund it. In less than a decade this would likely be a fairly easily attained amount of compute, nearly guaranteeing this attack.

## Recommendation
Verify with the factory that msg.sender is a valid pool i.e Change the verifyCallback to call factory.getPool to check that msg.sender is a Uniswap pool deployed by the factory.
