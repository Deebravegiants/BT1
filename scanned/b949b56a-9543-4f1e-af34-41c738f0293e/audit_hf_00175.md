# [H] `IndexPool.mint` The first liquidity provider is forced to supply assets in the same amount, which may cause a significant amount of fund loss

## Summary
Severity: High
Contest weight: 0.6178
Dataset id: 936
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When `reserve == 0`, `amountIn` for all the tokens will be set to the same amount: `ratio`, regardless of the weights, decimals and market prices of the assets.

The first liquidity provider may not be aware of this so that it may create an arbitrage opportunity for flashbots to take a significant portion of the value of The first liquidity provider’s liquidity.

[IndexPool.sol#L93 L105](https://github.com/sushiswap/trident/blob/6bd4c053b6213ffc612987eb565aa3813d5f0d13/contracts/pool/IndexPool.sol#L93-L105)

```solidity
/// @dev Mints LP tokens - should be called via the router after transferring `bento` tokens.
/// The router must ensure that sufficient LP tokens are minted by using the return value.
function mint(bytes calldata data) public override lock returns (uint256 liquidity) {
    (address recipient, uint256 toMint) = abi.decode(data, (address, uint256));

    uint120 ratio = uint120(_div(toMint, totalSupply));

    for (uint256 i = 0; i < tokens.length; i++) {
        address tokenIn = tokens[i];
        uint120 reserve = records[tokenIn].reserve;
        // @dev If token balance is '0', initialize with `ratio`.
        uint120 amountIn = reserve != 0 ? uint120(_mul(ratio, reserve)) : ratio;
        require(amountIn >= MIN_BALANCE, "MIN_BALANCE");
        // @dev Check Trident router has sent `amountIn` for skim into pool.
        unchecked {
            // @dev This is safe from overflow - only logged amounts handled.
            require(_balance(tokenIn) >= amountIn + reserve, "NOT_RECEIVED");
            records[tokenIn].reserve += amountIn;
        }
        emit Mint(msg.sender, tokenIn, amountIn, recipient);
    }
    _mint(recipient, toMint);
    liquidity = toMint;
}
```

## Recommendation
No recommendation
