### Title
`SimplexPaymaster` gas-price oracles have no L2 sequencer-uptime check, allowing mispriced gas charges during sequencer outages - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster._getOraclePrice` only checks a Chainlink answer's positivity and `updatedAt` staleness bound; it never verifies L2 sequencer liveness. The contract is deployed and priced with Chainlink feeds on multiple L2s with sequencers (Arbitrum, Optimism, Base — see `CHAINLINK_PRICE_FEED_CONTRACT_ADDRESSES`), so the classic Chainlink L2-sequencer-downtime issue applies directly to this gas-payment path.

### Finding Description
`_getOraclePrice` fetches `latestRoundData()` and only reverts on a non-positive answer or on `block.timestamp - updatedAt > maxOracleAge`: [1](#0-0) 

This is invoked from `_tokenPrice`, which is used by `_fetchDetails` during ERC-4337 validation of every UserOp routed through this paymaster: [2](#0-1) 

`_fetchDetails` is reached for any unprivileged UserOp sender — effectively a "bandwidth purchaser" paying gas in an ERC-20 stablecoin via this paymaster — with no permission gate on the caller. The same `_getOraclePrice`/`_tokenPrice` pair is also used in `swapAndDeposit` to compute `amountOutMin` for the treasury's fee-recycling swap: [3](#0-2) 

Per Chainlink's L2 documentation, when a sequencer goes down and later resumes, price feeds can report an answer that passes a simple `updatedAt` staleness check yet reflects stale market conditions (or a burst of catch-up updates), because the feed's heartbeat/updates are gated by the sequencer's own liveness, not just external round timing. The contract's `maxOracleAge` check does not substitute for the recommended `sequencerUptimeFeed` + `GRACE_PERIOD_TIME` check described in Chainlink's guidance, and no such check exists anywhere in `SimplexPaymaster.sol`. The addresses file confirms this paymaster's pricing model targets L2s with sequencers (Arbitrum `EVM-42161`, Optimism `EVM-10`, Base `EVM-8453`): [4](#0-3) 

### Impact Explanation
If the sequencer for a deployed L2 goes down and the token/USD or native/USD Chainlink feed reports a price that is stale relative to the true market but still within `maxOracleAge`, `_tokenPrice` will compute an incorrect ERC-20-per-wei-of-gas rate. Any unprivileged UserOp sender using the paymaster in that window is charged based on the wrong rate — either overcharging users (loss to users) or undercharging (paymaster insolvency/loss to the treasury, since ERC-20 proceeds no longer cover the native gas advanced by `EntryPoint`). The same stale price flows into `swapAndDeposit`'s `amountOutMin`, so the treasury's fee-recycling swap can execute at an incorrect minimum-output bound, causing an unfavorable swap that drains value that should have funded the paymaster's `EntryPoint` deposit. This is a Medium-severity, direct loss-of-funds condition rather than a purely theoretical one, matching the sherlock finding's classification.

### Likelihood Explanation
Sequencer downtime on Arbitrum, Optimism, and Base has occurred historically and is an explicitly documented risk Chainlink asks integrators to guard against for any L2 deployment. Since `SimplexPaymaster` is intended for deployment on these exact L2s (per the shared Chainlink-feed address table used by the SDK/indexer) and every UserOp validation depends on `_getOraclePrice`, the reachable surface is any ordinary user submitting a UserOp through the paymaster during a sequencer outage — no privileged role is required to trigger the mispricing.

### Recommendation
Add a Chainlink L2 sequencer-uptime feed check (as recommended in Chainlink's docs and as suggested in the original report for `ArbiChainlinkOracle.sol`) to `_getOraclePrice`, reverting when the sequencer is down or still inside its grace period after restart, e.g.:
```solidity
function isSequencerActive() internal view returns (bool) {
    (, int256 answer, uint256 startedAt,,) = sequencerUptimeFeed.latestRoundData();
    if (answer != 0) return false;
    if (block.timestamp - startedAt <= GRACE_PERIOD_TIME) return false;
    return true;
}
```
and call it at the top of `_getOraclePrice` (and thus transitively guard `_tokenPrice`, `_fetchDetails`, and `swapAndDeposit`), reverting with a dedicated error when the sequencer is unavailable.

### Proof of Concept
1. Deploy `SimplexPaymaster` on Arbitrum (or Optimism/Base) with a registered token whose Chainlink feed's `updatedAt` is within `maxOracleAge` but reflects a price from before the sequencer went offline.
2. Simulate sequencer downtime (or a documented historical outage window) where the underlying market price of the native asset or token has diverged materially from the last on-chain-reported round, while `updatedAt` still satisfies `block.timestamp - updatedAt <= maxOracleAge`.
3. Submit an ERC-4337 UserOp using this paymaster (mode `0x00` or `0x02`); `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` accepts the stale-but-"fresh" answer and computes an incorrect `tokenPrice`, causing the sender to be over- or under-charged relative to the true gas cost, or causing `swapAndDeposit`'s `amountOutMin` to be computed against the wrong rate, allowing the recycling swap to settle at a worse-than-intended price.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L454-480)
```text
    function swapAndDeposit(address token, uint256 amountIn) external {
        if (msg.sender != treasury) revert UnauthorizedCall();
        address router = IDispatcher(host()).uniswapV2Router();
        if (router == address(0)) revert InvalidRouter(router);
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amountIn == 0 || amountIn > balance) amountIn = balance;

        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;

        address[] memory path = new address[](2);
        path[0] = token;
        path[1] = IUniswapV2Router02(router).WETH();

        IERC20(token).forceApprove(router, amountIn);
        uint256[] memory amounts = IUniswapV2Router02(router)
            .swapExactTokensForETH(amountIn, amountOutMin, path, address(this), block.timestamp);

        uint256 deposited = address(this).balance;
        entryPoint().depositTo{value: deposited}(address(this));
        emit FeesRecycled(token, amountIn, amounts[1], deposited);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L524-546)
```text
    function _fetchDetails(
        PackedUserOperation calldata userOp,
        bytes32 /* userOpHash */
    )
        internal
        view
        override
        returns (uint256 validationData, IERC20 token, uint256 tokenPrice)
    {
        bytes calldata data = userOp.paymasterData();
        if (data.length < 21) revert InvalidPaymasterData(data.length);

        uint8 mode = uint8(data[0]);
        if (mode != 0x00 && mode != 0x02) revert InvalidMode(mode);

        address tokenAddr = address(bytes20(data[1:21]));

        TokenConfig memory cfg = tokenConfigs[tokenAddr];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(tokenAddr);
        if (!cfg.active) revert TokenNotActive(tokenAddr);

        tokenPrice = _tokenPrice(cfg);
        token = IERC20(tokenAddr);
```

**File:** evm/src/utils/SimplexPaymaster.sol (L662-676)
```text
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

**File:** sdk/packages/indexer/src/addresses/chainlink-price-feeds.addresses.ts (L10-13)
```typescript
	"EVM-1": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419", // Ethereum Mainnet
	"EVM-8453": "0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70", // Base Mainnet
	"EVM-10": "0x13e3Ee699D1909E989722E753853AE30b17e08c5", // Optimism Mainnet
	"EVM-42161": "0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612", // Arbitrum Mainnet
```
