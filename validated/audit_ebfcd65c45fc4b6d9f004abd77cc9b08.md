## Title
Paymaster prices ERC-20 gas payment using two independently-stale Chainlink oracles without timestamp synchronization - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._tokenPrice` computes the ERC-20 amount a UserOp sender must pay for gas by combining `nativeUsd` and `tokenUsd` from two separate Chainlink oracles, each validated only against its own independent `maxOracleAge` staleness bound with no requirement that the two readings be time-synchronized with each other, mirroring the analog bug class where a price derived from two independently-fresh-but-desynchronized cached quotes produces an inaccurate combined price.

### Finding Description
`_tokenPrice` fetches `nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals)` and `tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals)` and divides one by the other to derive `tokenPrice`: [1](#0-0) 

`_getOraclePrice` independently checks each oracle's own `updatedAt` against `block.timestamp - maxOracleAge`, but performs no comparison between the two oracles' `updatedAt` values: [2](#0-1) 

Because `maxOracleAge` can be governed as high as `MAX_ORACLE_AGE = 7 days` (and the contract's own comment notes some chains' feeds have "up to 24h" heartbeats), one oracle can legitimately report a value from `block.timestamp - maxOracleAge` seconds ago while the other reports a value from the current block, and both pass the staleness check individually. The two USD legs are then combined into a single ratio as if they were contemporaneous, exactly the "asset/base cached price timestamp desync" pattern from the report — except here the two legs are `nativeOracle` (used for the native/gas leg) and `tokenOracle` (used for the ERC-20 payment leg) rather than `assetTime`/`baseTime`.

This price is consumed directly by `_fetchDetails`, which any UserOp sender invokes on every validation to determine how much of the registered ERC-20 they must prefund for gas: [3](#0-2) 

### Impact Explanation
`tokenPrice` directly sets `erc20Cost = weiCost * tokenPrice / 1e18` inside `PaymasterERC20`, i.e., exactly how much ERC-20 is pulled from the sender (via `_prefund`/Permit2) to cover native gas. Any permissionless UserOp sender using this paymaster can time submission to a block where `nativeOracle` and `tokenOracle` are desynchronized in a favorable direction (e.g. token oracle stale-high relative to a freshly dropped native price, or vice versa), causing the paymaster to charge less ERC-20 than the true USD-equivalent gas cost. Since the paymaster's markup/treasury model relies on `tokenPrice` accurately reflecting current market rates, systematic exploitation of this desync drains value from the paymaster's collected token balance / EntryPoint deposit relative to actual gas spent, and conversely can overcharge senders in the opposite direction.

### Likelihood Explanation
This is reachable by any address able to submit an ERC-4337 UserOp through this paymaster — no special privilege is required — via the normal `_fetchDetails`/`_validatePaymasterUserOp` path used on every gas-sponsored operation. Divergence between two independent Chainlink feeds' `updatedAt` values within a shared `maxOracleAge` window is a routine occurrence (feeds update on different heartbeats/deviation thresholds), so the precondition for triggering an inaccurate combined price does not require an oracle failure or governance error — it can occur under normal market conditions, and a sender monitoring both feeds can select the block that yields the most favorable stale/fresh combination.

### Recommendation
Track and compare the `updatedAt` timestamps of both `nativeOracle` and `cfg.tokenOracle` in `_tokenPrice`/`_getOraclePrice`, and either (a) bound the allowed skew between the two `updatedAt` values (in addition to each one's own age check), or (b) use the older of the two timestamps as the effective staleness bound for the combined ratio, so `tokenPrice` is never derived from two USD legs whose observation times diverge beyond an acceptable window.

### Proof of Concept
1. Governance registers `tokenOracle` with a long heartbeat (e.g., ~24h, as anticipated by the contract's own comments) and `nativeOracle` with a short heartbeat (e.g., seconds/minutes), both under a shared `maxOracleAge` (e.g., set near `MAX_ORACLE_AGE`).
2. `tokenOracle.latestRoundData()` last updated near `block.timestamp - maxOracleAge` (still passing the individual staleness check) while the token's real-time market price has since moved unfavorably to the paymaster (e.g., token has appreciated since the stale reading, so the stale `tokenUsd` understates its true value).
3. `nativeOracle.latestRoundData()` is fresh (`updatedAt ≈ block.timestamp`), reflecting current native gas cost.
4. A sender submits a UserOp through this paymaster; `_tokenPrice` computes `tokenPrice = (freshNativeUsd * 10^tokenDecimals * (10000+markupBps)) / (staleTokenUsd * 10000)`, understating the required ERC-20 amount relative to the true current USD cost of gas because `staleTokenUsd` is lower than the token's real current price.
5. `_prefund` charges the sender the understated `prefundAmount`, and the paymaster's EntryPoint deposit is depleted by the real (higher) gas cost while collecting less-than-market-value ERC-20 in return — a repeatable value leak driven purely by legitimate, permissionless oracle timestamp desync rather than any oracle malfunction.

### Citations

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

**File:** evm/src/utils/SimplexPaymaster.sol (L653-658)
```text
    function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

        return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
    }
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
