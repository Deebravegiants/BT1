# [M] Improved Asset Price in PriceCalculator/NFTOracle

## Summary
Severity: Medium
Contest weight: 0.5938
Dataset id: 13384
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Whitehole protocol, the PriceCalculator contract maintains the price oracle for assets. While reviewing the logic to return the asset price to the caller, we notice it may return a invalid value, i.e.,
In the following, we show below the code snippet of the priceOfETH() routine, which is used to get the price of ETH. It first reads the latest price data from Chainlink if the price feed for ETH is available (line 130). Then if the price feed is unavailable, it refers to the reference price which is updated in one day by the admin (line 132). If neither of the price feed nor the reference price are available, it returns 0 as the price by default. However, it comes to our attention that 0 shall be an invalid price which may be used as a valid price by the caller if the caller does not properly validate it. As a result, the 0 asset price may lead to unexpected result to the lending markets. With that, we suggest to revert the price request when there is no available price exist in the PriceCalculator contract. Note the same issue is also applicable to the _oracleValueInUSDOf() routine.
```solidity
function priceOfETH()
    public
    view
    override
    returns (uint256 valueInUSD)
{
    valueInUSD = 0;
    if (tokenFeeds[ETH] != address(0)) {
        (,
         int price,
         ,
        ) = AggregatorV3Interface(tokenFeeds[ETH]).latestRoundData();
        return uint256(price).mul(1e10);
    } else if (references[ETH].lastUpdated > block.timestamp.sub(1 days)) {
        return references[ETH].lastData;
    }
    // Missing revert when no valid price exists
}
```
What's more, the Whitehole protocol provides the NFTOracle contract as the price oracle for NFT assets. The NFTOracle takes the floor price from NFT exchanges and calculates a time weighted average price (TWAP) per the history prices in the pre-defined TWAP interval (twapInterval).
In the following, we show the code snippet of the getUnderlyingPrice() routine, which is used to get the price for the given NFT. It first checks if the TWAP price for the NFT is available or not. If yes, it returns the TWAP price (line 178). Otherwise, it returns the latest configured floor price (line 176).
Our analysis shows that the TWAP price may be later than the latest configured price. In some rainy day case, this may expose arbitrage opportunity to arbitrager. For example, if there is a big price drop for the NFT, the TWAP price in the NFTOracle is much higher. So the arbitrager can buy the NFT with lower price and deposit it to Whitehole to borrow more ETH.
The Whitehole protocol properly introduces the design of floor price, collateral factor, borrow capacity and liquidation threshold for the NFT loan, which greatly mitigates the issue.
However, we still need to list the possibility of such arbitrage because of the price difference here and highly recommend project team to closely monitor the NFT price outside and adjust the protocol parameters (e.g., TWAP interval, collateral factor) to reduce the possibility of such arbitrage.
```solidity
function getUnderlyingPrice(address _gNft)
    external
    view
    override
    returns (uint256)
{
    address _nftContract = IGNft(_gNft).underlying();
    uint256 len = getPriceFeedLength(_nftContract);
    require(len > 0, "NFTOracle: no price data");
    uint256 twapPrice = twapPrices[_nftContract];
    if (twapPrice == 0)
        return nftPriceFeed[_nftContract].nftPriceData[len - 1].price;
    else
        return twapPrice;
}
```

## Recommendation
Revert when there is no available price in PriceCalculator, and closely monitor the NFT price outside to adjust NFT loan related parameters.
