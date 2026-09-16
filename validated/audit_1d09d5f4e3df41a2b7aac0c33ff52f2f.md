### Title
SimplexPaymaster prices gas in ERC-20 tokens from a raw Chainlink feed with no L2 sequencer-uptime/grace-period check - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` is a permissionless ERC-4337 paymaster reachable by any bandwidth purchaser (any account submitting a `PackedUserOperation` that pays gas in an ERC-20 token). It is explicitly documented as deployed on L2s such as Base as well as Ethereum/BSC, and converts gas cost to ERC-20 amounts using two raw Chainlink `AggregatorV3Interface.latestRoundData()` calls with only a staleness (`maxOracleAge`) and positivity check. It performs no check against an L2 sequencer uptime feed or a post-restart grace period.

### Finding Description
`_getOraclePrice` reads `latestRoundData()` and reverts only if the answer is non-positive or older than `maxOracleAge`: [1](#0-0) 

`_tokenPrice` combines the native/USD and token/USD oracle reads to compute the exchange rate used to charge users for gas, with no other sanity check: [2](#0-1) 

The contract's own documentation confirms multi-chain, including L2, deployment and per-chain heartbeat differences ("BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h"): [3](#0-2) 

On OP-Stack L2s such as Base, when the L1→L2 sequencer goes offline, the on-chain Chainlink price feed can stop updating or, once the sequencer restarts, immediately snap to a large delta reflecting all price movement missed during the outage. `maxOracleAge` alone does not protect against this: a heartbeat-compliant but stale-relative-to-market price can pass the staleness check right after sequencer restart, exactly the scenario Chainlink's L2 documentation recommends guarding against with a dedicated sequencer-uptime feed and grace period. `SimplexPaymaster` has no such check anywhere in its oracle-reading path, unlike battle-tested Chainlink consumer patterns.

### Impact Explanation
`_tokenPrice`/`_getOraclePrice` output is used directly to compute `getTokenPrice` and `estimateTokenCost`, which set the ERC-20 amount pulled from a user's permit/Permit2 allowance to prefund gas: [4](#0-3) 

If the native/USD or token/USD feed reports a stale-but-heartbeat-compliant price during or right after an L2 sequencer outage, the paymaster will charge users an incorrect token amount for gas: users could be overcharged (loss of user funds) or the paymaster could under-charge (loss of paymaster/treasury value, effectively a subsidized-gas drain across many UserOperations before governance can react via `UpdateParams`). Since this affects every UserOperation routed through the paymaster during the mispriced window, the effect scales with usage and constitutes concrete loss of funds for either the payer or the protocol's treasury, not merely a griefing/no-impact issue.

### Likelihood Explanation
Sequencer downtime on OP-Stack rollups (where this contract is explicitly designed to run, e.g., Base) has occurred historically and is a foreseeable, non-malicious-admin event. The condition requiring the exploit — a real price move occurring during an outage, publishable within the configured `maxOracleAge` window immediately upon sequencer restoration — does not require any privileged actor; it is triggered purely by normal UserOperation submission through the public paymaster interface, satisfying the "unprivileged bandwidth purchaser" reachability requirement.

### Recommendation
Add an L2 sequencer-uptime-feed check (Chainlink `SequencerUptimeFeed`) alongside the existing staleness check in `_getOraclePrice`/`_tokenPrice`, reverting or falling back when the sequencer is down or within the recommended grace period (e.g., 3600s) after it comes back up, mirroring Chainlink's documented "how to consume price feeds safely on L2" pattern. Consider also cross-checking with a secondary source (e.g., a TWAP from the Uniswap pool already integrated for `swapAndDeposit`) before accepting a price for fee computation.

### Proof of Concept
1. Deploy `SimplexPaymaster` on Base (or any OP-Stack chain) as intended per the contract's documentation.
2. Simulate the L1↔L2 sequencer going offline for a period during which the true BNB/ETH or token USD price moves significantly.
3. When the sequencer resumes, the Chainlink feed on L2 updates `updatedAt` to a recent timestamp with a price reflecting the full missed movement, passing `_getOraclePrice`'s `block.timestamp - updatedAt <= maxOracleAge` check trivially (since it is fresh).
4. Any UserOperation processed via `getTokenPrice`/`estimateTokenCost`/`_prefund` in this window is priced off this discontinuous jump, allowing under- or over-charging relative to the market price the moment before the outage, with no code path to detect or reject it (as `_getOraclePrice` never queries a sequencer uptime feed).

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L139-151)
```text
    struct Params {
        /// @notice Native asset / USD oracle (BNB/USD on BSC, ETH/USD on Ethereum, etc.)
        AggregatorV3Interface nativeOracle;
        /// @notice Markup in basis points (100 = 1%). Applied on top of the oracle price.
        uint256 markupBps;
        /// @notice Receives markup surplus and EntryPoint deposit withdrawals.
        address treasury;
        /// @notice Maximum oracle staleness. Chainlink heartbeats vary per chain
        ///         (BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h).
        uint256 maxOracleAge;
        /// @notice Slippage tolerance in basis points applied to the
        ///         oracle-derived expected output in {swapAndDeposit}.
        uint256 swapSlippageBps;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L653-658)
```text
    function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

        return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L660-676)
```text
    /// @dev Fetch a Chainlink price normalized to 8 decimals.
    ///      Reverts on stale or non-positive answers.
    function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
        (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();

        if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
        if (block.timestamp - updatedAt > maxOracleAge) {
            revert StaleOraclePrice(address(oracle), updatedAt);
        }

        if (oracleDecimals < 8) {
            return uint256(answer) * (10 ** (8 - oracleDecimals));
        } else if (oracleDecimals > 8) {
            return uint256(answer) / (10 ** (oracleDecimals - 8));
        }
        return uint256(answer);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L680-697)
```text
    /// @notice Current price in token base units per wei of gas (scaled by 1e18),
    ///         markup included. For offchain gas estimation.
    function getTokenPrice(address token) external view returns (uint256) {
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        return _tokenPrice(cfg);
    }

    /// @notice Estimate the token cost for a given gas amount and fee, mirroring
    ///         PaymasterERC20._erc20Cost (including its postOp gas cushion).
    function estimateTokenCost(address token, uint256 gasAmount, uint256 maxFeePerGas) external view returns (uint256) {
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        uint256 weiCost = gasAmount * maxFeePerGas + _postOpCost() * maxFeePerGas;
        return (weiCost * _tokenPrice(cfg)) / _tokenPriceDenominator();
    }
```
