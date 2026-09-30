# [M] Timely _updateCumuFundingRate During Pool Liquidity Changes

## Summary
Severity: Medium
Contest weight: 0.4594
Dataset id: 11878
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Similar to other perpetual protocols, the Deri protocol has a funding payment mechanism. Traders with open long or short positions will pay each other a funding payment, depending on market conditions. This incentivizes more traders to take the unpopular side of the trade. Speciﬁcally, four routines, i.e., _addLiquidity(), _removeLiquidity(), _withdrawMargin(), and trade() update the cumulative funding rate. In the _withdrawMargin() and trade() routines, the funding fee of the trader will be calculated. Conversely, _addLiquidity() and _removeLiquidity() routines only call _updateCumuFundingRate() after updating _liquidity. We notice an issue that attackers may make proﬁts by sending multiple transactions in a block to manipulate funding rate and trade. In particular, we show the related code snippet below. On its entry of _updateCumuFundingRate(), there is a check, i.e., if (block.number > _cumuFundingRateBlock). It ensures that _cumuFundingRate can only be modiﬁed once in a block. Furthermore, the result of rate is inﬂuenced by _tradersNetVolume, price, and _liquidity (line 682). In the _addLiquidity() routine, _liquidity is updated before _updateCumuFundingRate() (lines 575-577). Therefore, a malicious liquidity provider could intentionally manipulate the funding rate, and the other trade() transactions in the block can make proﬁts with that funding rate.
```solidity
function _updateCumuFundingRate(uint256 price) private {
    if (block.number > _cumuFundingRateBlock) {
        int256 rate;
        if (_liquidity != 0) {
            rate = _tradersNetVolume.mul(price).mul(_multiplier).mul(_fundingRateCoefficient).div(_liquidity);
        } else {
            rate = 0;
        }
        int256 delta = rate * (int256(block.number - _cumuFundingRateBlock));
        _cumuFundingRate += delta; // overflow intended
        _cumuFundingRateBlock = block.number;
    }
}

function _addLiquidity(uint256 bAmount) internal _lock_ {
    require(bAmount >= _minAddLiquidity, "PerpetualPool: add liquidity less than minimum requirement");
    require(bAmount.reformat(_bDecimals) == bAmount, "PerpetualPool: _addLiquidity bAmount not valid");
    _bToken.safeTransferFrom(msg.sender, address(this), bAmount.rescale(_bDecimals));
    uint256 poolDynamicEquity = _liquidity.add(_tradersNetCost.sub(_tradersNetVolume.mul(_price).mul(_multiplier)));
    uint256 totalSupply = _lToken.totalSupply();
    uint256 lShares;
    if (totalSupply == 0) {
        lShares = bAmount;
    } else {
        lShares = bAmount.mul(totalSupply).div(poolDynamicEquity);
    }
    _lToken.mint(msg.sender, lShares);
    _liquidity = _liquidity.add(bAmount);
    _updateCumuFundingRate(_price);
    emit AddLiquidity(msg.sender, lShares, bAmount);
}
```

## Recommendation
Update _CumuFundingRate timely in _addLiquidity() and _removeLiquidity().
