# [M] Functions that rely on chainlink prices cannot be queried on avalanche due to sequencer uptime check.

## Summary
Severity: Medium
Contest weight: 0.5935
Dataset id: 9793
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Avalanche unlike Arbitrum needs no sequencer uptime check. As a result, checking for uptime feeds when validating price will cause the function to always revert.

Also, the sequencerUptimeFeed address is hardcoded to an address specific only to arbitrum.

Vulnerability Details
In KeeperProxy.sol, _validatePrice performs an L2 sequencer check. This check will break on avalanche, as the chain doesn't have a sequencer, or require a sequencer check.

```solidity
  function _validatePrice(address perpVault, MarketPrices memory prices) internal view {
// L2 Sequencer check
    (
      uint80 roundID,
      int256 answer,
      uint256 startedAt,
      uint256 updatedAt,
      uint80 answeredInRound
    ) = AggregatorV2V3Interface(sequencerUptimeFeed).latestRoundData();
    bool isSequencerUp = answer == 0;
    require(isSequencerUp, "sequencer is down");
    // Make sure the grace period has passed after the sequencer is back up.
    uint256 timeSinceUp = block.timestamp - startedAt;
    require(timeSinceUp > GRACEPERIODTIME, "Grace period is not over");

    address market = IPerpetualVault(perpVault).market();
    IVaultReader reader = IPerpetualVault(perpVault).vaultReader();
    MarketProps memory marketData = reader.getMarket(market);
    
    _check(marketData.indexToken, prices.indexTokenPrice.min);
    _check(marketData.indexToken, prices.indexTokenPrice.max);
    _check(marketData.longToken, prices.indexTokenPrice.min);
    _check(marketData.longToken, prices.indexTokenPrice.max);
    _check(marketData.shortToken, prices.shortTokenPrice.min);
    _check(marketData.shortToken, prices.shortTokenPrice.max);
  }
```

Doing this regardless of whatever sequencerUptimeFeed is set will cause the function to always revert (even if none is set).

Also, when KeeperProxy.sol is initialized, the sequencerUptimeFeed is hardcoded to 0xFdB631F5EE196F0ed6FAa767959853A9F217697D. On arbitrum, this is the correct address, but on avalanche, the address is non-existent.

```solidity
  function initialize() external initializer {
    _Ownable2Stepinit();
    sequencerUptimeFeed = AggregatorV2V3Interface(0xFdB631F5EE196F0ed6FAa767959853A9F217697D);
  }
```

Impact
As a result, _validatePrice and all of its dependent functions, e.g run, runNextAction will always fail upon deployment to avalanche.

Tools Used
Manual Review

Recommendations
Introduce a check for chainId in the _validatePrice function, if chainId is that of avalanche, skip the sequencer check.

In KeeperProxy.sol, _validatePrice performs an L2 sequencer check. This check will break on avalanche, as the chain doesn't have a sequencer, or require a sequencer check.

```solidity
  function _validatePrice(address perpVault, MarketPrices memory prices) internal view {
// L2 Sequencer check
    (
      uint80 roundID,
      int256 answer,
      uint256 startedAt,
      uint256 updatedAt,
      uint80 answeredInRound
    ) = AggregatorV2V3Interface(sequencerUptimeFeed).latestRoundData();
    bool isSequencerUp = answer == 0;
    require(isSequencerUp, "sequencer is down");
    // Make sure the grace period has passed after the sequencer is back up.
    uint256 timeSinceUp = block.timestamp - startedAt;
    require(timeSinceUp > GRACEPERIODTIME, "Grace period is not over");

    address market = IPerpetualVault(perpVault).market();
    IVaultReader reader = IPerpetualVault(perpVault).vaultReader();
    MarketProps memory marketData = reader.getMarket(market);
    
    _check(marketData.indexToken, prices.indexTokenPrice.min);
    _check(marketData.indexToken, prices.indexTokenPrice.max);
    _check(marketData.longToken, prices.indexTokenPrice.min);
    _check(marketData.longToken, prices.indexTokenPrice.max);
    _check(marketData.shortToken, prices.shortTokenPrice.min);
    _check(marketData.shortToken, prices.shortTokenPrice.max);
  }
```

Doing this regardless of whatever sequencerUptimeFeed is set will cause the function to always revert (even if none is set).

Also, when KeeperProxy.sol is initialized, the sequencerUptimeFeed is hardcoded to 0xFdB631F5EE196F0ed6FAa767959853A9F217697D. On arbitrum, this is the correct address, but on avalanche, the address is non-existent.

```solidity
  function initialize() external initializer {
    _Ownable2Stepinit();
    sequencerUptimeFeed = AggregatorV2V3Interface(0xFdB631F5EE196F0ed6FAa767959853A9F217697D);
  }
```

Impact
As a result, _validatePrice and all of its dependent functions, e.g run, runNextAction will always fail upon deployment to avalanche.

Tools Used
Manual Review

Recommendations
Introduce a check for chainId in the _validatePrice function, if chainId is that of avalanche, skip the sequencer check.

As a result, _validatePrice and all of its dependent functions, e.g run, runNextAction will always fail upon deployment to avalanche.

Tools Used
Manual Review

Recommendations
Introduce a check for chainId in the _validatePrice function, if chainId is that of avalanche, skip the sequencer check.

## Recommendation
Introduce a check for chainId in the _validatePrice function, if chainId is that of avalanche, skip the sequencer check.
