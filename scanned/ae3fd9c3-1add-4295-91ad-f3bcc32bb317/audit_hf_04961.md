# [M] Manager can mint performance fees even when

## Summary
Severity: Medium
Contest weight: 0.5976
Dataset id: 22921
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Manager can mint performance fees even when token price decreases overall. Managers of funds are entitled to 2 types of fees: performance fees and streaming fees.
s/PoolLogic.sol#L694-L720
```solidity
uint256 streamingFee = _tokenSupply.mul(timeChange).mul(_managerFeeNumerator).div(_feeDenominator).div(365 days);
```
Performance fees are more complicated. They are only extracted when the fund performs well and creates a profit for the end user and the manager gets minted a part of it.
```solidity
uint256 currentTokenPrice = _fundValue.mul(10 ** 18).div(_tokenSupply);
if (currentTokenPrice > tokenPriceAtLastFeeMint) {
    available = currentTokenPrice
        .sub(tokenPriceAtLastFeeMint)
        .mul(_tokenSupply)
        .mul(_performanceFeeNumerator)
        .div(_feeDenominator)
        .div(currentTokenPrice);
}
```
These fees are not token transfers, rather they are minted an equivalent number of shares, which the managers can they redeem to get the actual fees in the underlying tokens. Since the fees are distributed in the form of freshly minted shares, minting the manager fee decreases the tokenPrice of the fund. The tokenPrice is the ratio of the fund value to the total number of shares.
```solidity
uint256 currentTokenPrice = _fundValue.mul(10 ** 18).div(_tokenSupply);
```
When fee shares are minted, the _fundValue remains the same, but the _tokenSupply increases, which decreases the tokenPrice. The issue is that in certain situations, managers can collect performance fees even if the token price decreases overall. Lets say a fund has 1000 dollars of tokens and 1000 shares minted. the starting tokenPrice is therefore 1e18. After a year, lets say the fund grew 4%, to a now value of 1040 dollars. Lets assume the streaming fee is 5% and the performance fee is 20%. When calculating the manager fees, the currentTokenPrice is now calculated as 1040 * 1e18 / 1000 = 1.04e18, so a potential profit! So the manager gets minted their performance shares = 40 * 1000 * 20/100 / 1040 = 7.69 shares. Further, they also get minted the streaming fee shares = 1000*5/100 = 50 shares. So the manager gets minted 57.69 shares in total, and the totalSupply of the fund now grows to 1057.69 shares. For the end user, the fund value before the manager fee mint was 1e18. After the fee mint, their fund value is 1040 * 1e18 / 1057.69 = 0.983e18. So for the end users, the tokenValue has actually decreased while they are still charged a performance fee. Furthermore, the tokenPriceAtLastFeeMint is updated only if the tokenprice rises after the mint.
```solidity
if (daoFee > 0) _mint(daoAddress, daoFee);
if (managerFee > 0) _mint(manager(), managerFee);
uint256 currentTokenPrice = _tokenPrice(fundValue, tokenSupply);
if (tokenPriceAtLastFeeMint < currentTokenPrice) {
    tokenPriceAtLastFeeMint = currentTokenPrice;
}
```
In this case, since the token price did not rise, they tokenPriceAtLastFeeMint stays the same (1e18), and the manager will be minted performance fees again if they beat the target of 1e18. This is unfair, since the manager already collected fees based on the assumption that they beat the target already last term with the new price of 1.04e18. So in essence, if streaming fees are higher than the fund growth, the manager can keep beating the same old target over and over and keep collecting performance fees. The end user are not able to capture any part of this growth, and thus keeps seeing their holding values decrease over time even though their manager is collecting performance based bonuses. Manager can beat the same target multiple times and keep collecting performance fees without updating the target. Users dont get a loss, while the manager collects performance fees.

## Recommendation
Update the tokenPriceAtLastFeeMint to the tokenprice used for bonus calculation, and not the current price after share dilution. In the above example, the tokenPriceAtLastFeeMint should be set to 1.04e18, so that way the manager has to hit this new price target in order to collect performance fees in the next year. This will prevent managers from collecting performance fees with the same target year over year.
