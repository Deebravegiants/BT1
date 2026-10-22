# [H] Public Exposure of Privileged Functions

## Summary
Severity: High
Contest weight: 0.6378
Dataset id: 12417
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The audited LogX protocol is a unique decentralized derivative exchange. To facilitate the trading and position management, the protocol has a number of privileged functions. While examining these privileged functions, we notice some of them are publicly exposed without caller verification. In the following, we show an example privileged routine from the PriceFeed contract. This routine is designed to configure the latest asset price. However, this routine is public and its public exposure without any caller authentication will corrupt the protocol integrity or cripple the entire protocol functionality.
```solidity
function _setPrice(address _tokenAddress, PriceArgs memory _darkOraclePrice) public
    validateData(_darkOraclePrice.publishTime);
    TokenPrice memory priceObject = TokenPrice(_darkOraclePrice.price, _darkOraclePrice.price, _darkOraclePrice.expo, _darkOraclePrice.expo, _darkOraclePrice.publishTime);
    tokenToPrice[_tokenAddress] = priceObject;
    emit PriceSet(priceObject);
}

function compareAndSetPrice(address _tokenAddress, PythStructs.Price memory _pythPrice, PriceArgs memory _darkOraclePrice) public {
    uint256 pythPrice = getFinalPrice(uint64(_pythPrice.price), _pythPrice.expo);
    uint256 darkOraclePrice = getFinalPrice(uint64(_darkOraclePrice.price), _darkOraclePrice.expo);
    if (allowedDelta(pythPrice, darkOraclePrice)) {
        _setPrice(_tokenAddress, _darkOraclePrice);
    } else {
        validateData(_pythPrice.publishTime);
        TokenPrice memory priceObject = TokenPrice(
            pythPrice > darkOraclePrice ? uint64(_pythPrice.price) : _darkOraclePrice.price,
            pythPrice < darkOraclePrice ? uint64(_pythPrice.price) : _darkOraclePrice.price,
            pythPrice > darkOraclePrice ? _pythPrice.expo : _darkOraclePrice.expo,
            pythPrice < darkOraclePrice ? _pythPrice.expo : _darkOraclePrice.expo,
            _darkOraclePrice.publishTime
        );
        tokenToPrice[_tokenAddress] = priceObject;
        emit PriceSet(priceObject);
    }
}
```

## Recommendation
Revisit all public functions and add necessary caller verification. Note this issue affects a few public functions, including RewardTracker::setRewardPrecision().
