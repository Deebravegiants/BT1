# [M] No check for active L2 Sequencer

## Summary
Severity: Medium
Contest weight: 0.4590
Dataset id: 20395
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Using Chainlink in L2 chains such as Arbitrum requires to check if the sequencer is
down to avoid prices from looking like they are fresh although they are not
according to their recommendation
The SingleSidedLPVaultBase and CrossCurrencyVault contracts make the
getOraclePrice external call to the TradingModule contract. However, the
getOraclePrice in the TradingModule makes no check to see if the sequencer is
down.
If the sequencer goes down, the protocol will allow users to continue to operate at
the previous (stale) rates and this can be leveraged by malicious actors to gain
unfair advantage.
718e7f9128f845e10f02/leveraged-vaults/contracts/vaults/common/SingleSidedLP
VaultBase.sol#L323
function _getOraclePairPrice(address base, address quote) internal view returns
(uint256) {
    (int256 rate, int256 precision) = TRADING_MODULE.getOraclePrice(base, quote);
    require(rate > 0);
    require(precision > 0);
    return uint256(rate) * POOL_PRECISION() / uint256(precision);
}
718e7f9128f845e10f02/leveraged-vaults/contracts/vaults/CrossCurrencyVault.sol
#L131
(int256 rate, int256 rateDecimals) = TRADING_MODULE.getOraclePrice(
718e7f9128f845e10f02/leveraged-vaults/contracts/trading/TradingModule.sol#L71
C1-L77C6
function getOraclePrice(address baseToken, address quoteToken)
public
view
override
returns (int256 answer, int256 decimals)
{
    PriceOracle memory baseOracle = priceOracles[baseToken];
    PriceOracle memory quoteOracle = priceOracles[quoteToken];
    int256 baseDecimals = int256(10**baseOracle.rateDecimals);
    int256 quoteDecimals = int256(10**quoteOracle.rateDecimals);
    (/* */, int256 basePrice, /* */, uint256 bpUpdatedAt, /* */) =
    baseOracle.oracle.latestRoundData();
    require(block.timestamp - bpUpdatedAt <= maxOracleFreshnessInSeconds);
    require(basePrice > 0); /// @dev: Chainlink Rate Error
    (/* */, int256 quotePrice, /* */, uint256 qpUpdatedAt, /* */) =
    quoteOracle.oracle.latestRoundData();
    require(block.timestamp - qpUpdatedAt <= maxOracleFreshnessInSeconds);
    require(quotePrice > 0); /// @dev: Chainlink Rate Error
    answer =
    (basePrice * quoteDecimals * RATE_DECIMALS) /
    (quotePrice * baseDecimals);
    decimals = RATE_DECIMALS;
}
```

## Recommendation
It is recommended to follow the Chailink example code
