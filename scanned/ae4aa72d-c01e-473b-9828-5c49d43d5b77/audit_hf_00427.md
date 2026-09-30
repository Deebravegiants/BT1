# [M] Mixed Token Price Will Be Inaccurate Due to Decimal Miscalculation in MixOracle

## Summary
Severity: Medium
Contest weight: 0.6923
Dataset id: 1839
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MixOracle::getThePrice() function contains a logical error, causing the calculated price of a token to be incorrectly inflated or deflated. This issue arises when token pairs with differing decimal scales are used, leading to inaccurate pricing data.
1. The problem lies in the following function:
V3-Contracts/contracts/oracles/MixOracle/MixOracle.sol#L40-L70
```solidity
function getThePrice(address tokenAddress) public returns (int) {
    // get tarotOracle address
    address _priceFeed = AttachedTarotOracle[tokenAddress];
    require(_priceFeed != address(0), "Price feed not set");
    require(!isPaused, "Contract is paused");
    ITarotOracle priceFeed = ITarotOracle(_priceFeed);
    address uniswapPair = AttachedUniswapPair[tokenAddress];
    require(isFeedAvailable[uniswapPair], "Price feed not available");
    // get twap price from token1 in token0
    (uint224 twapPrice112x112, ) = priceFeed.getResult(uniswapPair);
    address attached = AttachedPricedToken[tokenAddress];
    // Get the price from the pyth contract, no older than 20 minutes
    // get usd price of token0
    int attachedTokenPrice = IPyth(debitaPythOracle).getThePrice(attached);
    uint decimalsToken1 = ERC20(attached).decimals();
    uint decimalsToken0 = ERC20(tokenAddress).decimals();
    // calculate the amount of attached token that is needed to get 1 token1
    int amountOfAttached = int(
        ((2 ** 112)) * (10 ** decimalsToken1)) / twapPrice112x112
    );
    // calculate the price of 1 token1 in usd based on the attached token
    uint price = (uint(amountOfAttached) * uint(attachedTokenPrice)) /
        (10 ** decimalsToken1);
    require(price > 0, "Invalid price");
    return int(uint(price));
}
```
Here, decimalsToken1 is mistakenly used for scaling instead of decimalsToken0 in line 66. This discrepancy is critical when the token pair has different decimals. Furthermore, the variable decimalsToken0 is defined but not utilized anywhere else in the function, highlighting a clear logical oversight.
Internal pre-conditions
The admin sets token pairs in the MixOracle where the tokens have differing decimals (e.g., USDC with 6 decimals and DAI with 18 decimals).
External pre-conditions
Attack Path
1. Assume MixOracle::getThePrice() is called with tokenAddress = DAI.
2. In the contract:
• decimalsToken0 = 1e18 (DAI has 18 decimals).
• decimalsToken1 = 1e6 (USDC has 6 decimals).
3. Due to the logical error in line 66, the token price will be inflated by 1e12 (or deflated in other cases), depending on the tokens in the pair.
4. This incorrect price propagation may result in:
• Incorrect exchange rates.
• Loss of funds for users or systems relying on this data.
Mix oracle get the inflated/deflated price, leading to the loss of funds.

## Recommendation
In line 61, replace decimalsToken1 with decimalsToken0.
```solidity
uint price = (uint(amountOfAttached) * uint(attachedTokenPrice)) /
    (10 ** decimalsToken1);
```
should be:
```solidity
uint price = (uint(amountOfAttached) * uint(attachedTokenPrice)) /
    (10 ** decimalsToken0);
```
