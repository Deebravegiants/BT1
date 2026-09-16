## Title
`SimplexPaymaster` prices gas via Chainlink feeds without checking the Arbitrum/L2 sequencer uptime feed - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster._getOraclePrice` only checks a Chainlink feed's `updatedAt` staleness bound; it never verifies that the L2 sequencer is up, per Chainlink's documented pattern for L2 deployments (sequencer uptime feed + grace period). `SimplexPaymaster` is intended to be deployed permissionlessly across many chains — the deployment script and indexer address tables explicitly include Arbitrum (`EVM-42161`) alongside Ethereum/Base/Optimism/BSC — so this L2-specific gap is directly reachable in production.

### Finding Description
`_getOraclePrice` is the sole gate on Chainlink data used to price gas payments: [1](#0-0) 

It reverts only on a non-positive answer or on staleness relative to `maxOracleAge`; there is no call to an L2 sequencer uptime feed (`0xFdB631F5EE196F0ed6FAa767959853A9F217697D`-style feed) and no grace-period check after a sequencer restart, unlike the pattern Chainlink recommends for Arbitrum/Optimism/Base deployments. This price feeds both the per-UserOp cost computation (`_tokenPrice`, used in `getTokenPrice`/`estimateTokenCost` and the actual `_erc20Cost` charged during `_postOp`) and the swap-slippage bound in `swapAndDeposit`: [2](#0-1) 

The deployment script confirms this contract is meant to be deployed with arbitrary chain-specific oracle addresses (native oracle + per-token oracles) read from a generic config, with no chain-specific handling for L2 sequencer risk: [3](#0-2) 

and Arbitrum is a first-class supported chain elsewhere in the stack (e.g. Chainlink price-feed address tables list `EVM-42161` for Arbitrum Mainnet): [4](#0-3) 

When the Arbitrum sequencer goes down, the last on-chain Chainlink update on L2 can appear "fresh" (within `maxOracleAge`) for an extended period because no new L2 blocks/timestamps are advancing to trigger the staleness check the same way it would off-chain, and once the sequencer comes back there is a well-known period where force-included L1 transactions or a burst of stale price reporting can produce incorrect prices. `_getOraclePrice` has no defense against either condition.

### Impact Explanation
An incorrect or stale price accepted during/around a sequencer outage directly changes how much ERC-20 stablecoin a UserOp sender is charged for a given amount of native gas via `_tokenPrice`/`_erc20Cost` in the ERC-4337 `_postOp` flow, and also sets the `amountOutMin` floor for `swapAndDeposit`'s Uniswap swap of accrued fees. A mispriced native/USD or token/USD ratio during this window lets UserOp senders systematically underpay for gas (protocol/treasury value drain) or lets a treasury-triggered swap execute at an incorrect floor, i.e., concrete loss of funds accruing to the paymaster/treasury — a Medium-severity oracle-manipulation-adjacent finding matching the class of the reported issue.

### Likelihood Explanation
Sequencer outages are infrequent but have occurred on Arbitrum before (as cited in the source report) and this contract is explicitly designed for multi-chain, permissionless deployment including Arbitrum. Any ordinary, unprivileged UserOp sender can trigger the mispriced path simply by submitting a UserOp during the outage/recovery window — no special privilege or governance action is required.

### Recommendation
Add an L2 sequencer-uptime-feed check (per Chainlink's `L2SequencerUptimeFeed` pattern) to `_getOraclePrice`, requiring `answer == 0` (up) and enforcing a grace period after `startedAt` before trusting price data, configurable per chain in `Params`/`TokenConfig` similar to `maxOracleAge`.

### Proof of Concept
1. Deploy `SimplexPaymaster` on Arbitrum with `nativeOracle`/token oracles pointing at real Chainlink ETH/USD and USDC/USD feeds, per `DeploySimplexPaymaster.s.sol`.
2. Simulate an Arbitrum sequencer outage (as in the referenced 10-hour outage): the last `latestRoundData().updatedAt` recorded on-chain stops advancing but stays within `maxOracleAge` for the outage duration.
3. Submit a UserOp through the paymaster during this window; `_getOraclePrice` returns the stale price without reverting because only `block.timestamp - updatedAt > maxOracleAge` is checked, and `_erc20Cost`/`_postOp` charge the sender based on this stale/incorrect valuation.
4. Repeat during the sequencer-recovery burst, where price data may momentarily reflect the L1 force-inclusion queue rather than a consistent, sequenced price — again accepted without a grace-period check.

### Citations

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

**File:** evm/script/DeploySimplexPaymaster.s.sol (L31-52)
```text
        if (hasUsdt) {
            tokens[1] = config.get("USDT_TOKEN").toAddress();
            oracles[1] = AggregatorV3Interface(config.get("USDT_ORACLE").toAddress());
        }

        SimplexPaymaster implementation = new SimplexPaymaster{salt: salt}();
        bytes memory initData = abi.encodeCall(
            SimplexPaymaster.initialize,
            (
                HOST_ADDRESS,
                SimplexPaymaster.Params({
                    nativeOracle: AggregatorV3Interface(nativeOracleAddr),
                    markupBps: markupBps,
                    treasury: treasury,
                    maxOracleAge: maxOracleAge,
                    swapSlippageBps: swapSlippageBps
                }),
                tokens,
                oracles,
                relayer
            )
        );
```

**File:** sdk/packages/indexer/src/addresses/chainlink-price-feeds.addresses.ts (L13-13)
```typescript
	"EVM-42161": "0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612", // Arbitrum Mainnet
```
