# [M] Oracle - Unchecked oracle response timestamp and integer over/underflow

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The external Chainlink oracle, which provides index price information to the system, introduces risk inherent to any dependency on third-party data sources. For example, the oracle could fall behind or otherwise fail to be maintained, resulting in outdated data being fed to the index price calculations of the AMM. Oracle reliance has historically resulted in crippled on-chain systems, and complications that lead to these outcomes can arise from things as simple as network congestion.

Ensuring that unexpected oracle return values are properly handled will reduce reliance on off-chain components and increase the resiliency of the smart contract system that depends on them.

#### Examples

1. The `ChainlinkAdapter` and `InversedChainlinkAdapter` take the oracle's (int256) `latestAnswer` and convert the result using `chainlinkDecimalsAdapter`. This arithmetic operation can underflow/overflow if the Oracle provides a large enough answer:


**code/contracts/oracle/ChainlinkAdapter.sol:L10-L19**
```solidity
int256 public constant chainlinkDecimalsAdapter = 10**10;

constructor(address _feeder) public {
    feeder = IChainlinkFeeder(_feeder);
}

function price() public view returns (uint256 newPrice, uint256 timestamp) {
    newPrice = (feeder.latestAnswer() * chainlinkDecimalsAdapter).toUint256();
    timestamp = feeder.latestTimestamp();
}
```


**code/contracts/oracle/InversedChainlinkAdapter.sol:L11-L20**
```solidity
int256 public constant chainlinkDecimalsAdapter = 10**10;

constructor(address _feeder) public {
    feeder = IChainlinkFeeder(_feeder);
}

function price() public view returns (uint256 newPrice, uint256 timestamp) {
    newPrice = ONE.wdiv(feeder.latestAnswer() * chainlinkDecimalsAdapter).toUint256();
    timestamp = feeder.latestTimestamp();
}
```

2. The oracle provides a timestamp for the `latestAnswer` that is not validated and may lead to old oracle timestamps being accepted (e.g. caused by congestion on the blockchain or a directed censorship attack).


**code/contracts/oracle/InversedChainlinkAdapter.sol:L19-L20**
```solidity
    timestamp = feeder.latestTimestamp();
}
```

#### Recommendation

* Use `SafeMath` for mathematical computations

* Verify `latestAnswer` is within valid bounds (`!=0`)

* Verify `latestTimestamp` is within accepted bounds (not in the future, was updated within a reasonable amount of time)

* Deduplicate code by combining both Adapters into one as the only difference is that the `InversedChainlinkAdapter` returns `ONE.wdiv(price)`.
