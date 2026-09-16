### Title
Missing L2 Sequencer uptime check in `SimplexPaymaster`'s Chainlink price consumption - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._getOraclePrice` consumes Chainlink `AggregatorV3Interface.latestRoundData()` directly and only guards against a stale/non-positive answer via `updatedAt` and `answer <= 0`; it never checks an L2 Sequencer Uptime Feed. [1](#0-0)  The paymaster is explicitly designed to price ERC-4337 gas prefunds in stablecoins using `nativeOracle`/`tokenOracle` Chainlink feeds and is meant to run on the same set of chains Hyperbridge already supports as L2 rollups (Arbitrum, Optimism, Base), per the fisherman/registry L2 chain lists. [2](#0-1) 

### Finding Description
`_getOraclePrice` is the sole gate on price data used throughout the contract's economic logic (`_tokenPrice`, `getTokenPrice`, `estimateTokenCost`, `swapAndDeposit`, and — critically — `_fetchDetails`/`_prefund`, which determine how much of a solver's/UserOp sender's ERC-20 is pulled to prefund gas): [3](#0-2) 

The staleness check (`block.timestamp - updatedAt > maxOracleAge`) is a heartbeat check, not a sequencer-liveness check. On Arbitrum/Optimism-style L2s, Chainlink explicitly recommends consulting a dedicated `Sequencer Uptime Feed` in addition to the price feed's own heartbeat, because:
1. While the sequencer is down, price feed updates on the L2 can silently stop advancing even though `updatedAt` may still look "fresh enough" relative to `maxOracleAge` (a 7-day cap is allowed, `MAX_ORACLE_AGE = 7 days`, and `Params.maxOracleAge` for a stablecoin pair is configured up to 24h per the code's own comment). [4](#0-3) [5](#0-4) 
2. Immediately after the sequencer resumes, feeds can report a burst of stale/incorrect values during the "grace period" before Chainlink nodes resynchronize — a widely-documented misuse vector when this check is skipped.

Because `_getOraclePrice` is used to compute both `nativeUsd` and `tokenUsd` for `_tokenPrice(cfg)`, and `_tokenPrice` directly feeds `_erc20Cost(maxCost, userOp.maxFeePerGas(), tokenPrice)` in `_prefund`, a stale/incorrect price during Sequencer downtime or its grace period lets any permissionless ERC-4337 sender (including intent solvers, per the contract's own security notes about "solver accounts" and "a malicious oracle") prefund gas at a mispriced rate. [6](#0-5) [7](#0-6) 

### Impact Explanation
If a stale-but-not-yet-expired price understates the native gas price relative to the token, users pay less ERC-20 than the actual gas cost, draining the paymaster's `EntryPoint` deposit/treasury reserves over repeated transactions until governance intervenes (`UpdateParams`/`DeactivateToken` are the only mitigations, and both are governance-latency-bound onAccept flows, not automatic). Conversely, an overstated price causes users to overpay, effectively "stealing" from users' prefunded balances. `swapAndDeposit` also relies on the same unchecked oracle price to compute `amountOutMin`, so a stale/incorrect price there can push an unfavorable swap through governance-triggered fee recycling. [8](#0-7)  This is a concrete funds-drain/mispricing vector reachable by any unprivileged UserOp sender (including intent-fill solvers using this paymaster to pay gas), matching the "concrete theft ... of funds" bar.

### Likelihood Explanation
Likelihood depends on: (a) `SimplexPaymaster` actually being deployed on an L2 with a sequencer (Arbitrum/Optimism/Base — all chains Hyperbridge already tracks as L2 rollups), and (b) an actual sequencer outage or restart-grace-period occurring while `maxOracleAge` (configurable up to `MAX_ORACLE_AGE = 7 days`, with stablecoin feeds documented up to 24h) has not yet elapsed. Sequencer outages on major L2s, while infrequent, have occurred historically (e.g., past Arbitrum/Optimism multi-hour outages), and the 24h staleness allowance for stablecoin pairs on Base/Ethereum comfortably covers typical outage windows, making exploitation plausible rather than purely theoretical.

### Recommendation
Add an L2 Sequencer Uptime Feed check (per Chainlink's documented pattern) in `_getOraclePrice`, reverting or falling back to a safe path if the sequencer is down or within a grace period (e.g., 1 hour) after it comes back up, before trusting `latestRoundData()` from the price oracle(s). This should gate both the `nativeOracle` and per-token `tokenOracle` reads used across `_tokenPrice`, `getTokenPrice`, `estimateTokenCost`, and `swapAndDeposit`.

### Proof of Concept
1. `SimplexPaymaster` is deployed and configured on an L2 (e.g., Arbitrum) with `nativeOracle`/`tokenOracle` set to that chain's Chainlink feeds and `maxOracleAge` set near the allowed ceiling for a stablecoin pair (up to 24h, per the contract's own documentation comment).
2. The L2 sequencer goes offline; L2 Chainlink feed updates stop advancing but `updatedAt` remains within `maxOracleAge` for the duration of the outage (bounded well under 24h for many historical outages).
3. During the outage (or immediately after, during the Chainlink resync grace period), an attacker submits a UserOp through `SimplexPaymaster` using the frozen/incorrect price: `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` returns the stale price without reverting (since only `updatedAt`-based staleness is checked), and `_prefund`/`_erc20Cost` charges the attacker the mispriced amount.
4. Repeating this while the sequencer is down/recovering drains the paymaster's stablecoin surplus/EntryPoint deposit relative to actual gas expenditure, or overcharges honest users, depending on price-skew direction.

Note: I was unable to confirm from the indexed code exactly which chain(s) `SimplexPaymaster` is deployed to in production (deployment scripts/configs were not found in the indexed context), so likelihood is stated conditionally on an L2 (sequencer-based) deployment — this is corroborated by the contract's chain-agnostic design (comments explicitly reference BSC, Base, Ethereum) and Hyperbridge's broader support for Arbitrum/Optimism/Base as L2s elsewhere in the codebase.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L84-93)
```text
/// @dev Security model. The only allowance a solver ever holds towards this
///      contract is the residue of a mode 0x00 permit, bounded by the signed
///      permitAmount; mode 0x02 leaves none. A compromise must never translate
///      into large withdrawals from solver accounts. There is no privileged
///      key: every administrative action — upgrades, parameter changes, token
///      registry, withdrawals — is an onAccept request authenticated as
///      originating from Hyperbridge governance and delivered by the local
///      host. Clients additionally keep permit amounts small (a few dollars),
///      bounding exposure to the residual allowance even against a malicious
///      oracle.
```

**File:** evm/src/utils/SimplexPaymaster.sol (L146-148)
```text
        /// @notice Maximum oracle staleness. Chainlink heartbeats vary per chain
        ///         (BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h).
        uint256 maxOracleAge;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L164-165)
```text
    /// @dev Hard ceiling on the governance-configurable oracle staleness bound.
    uint256 public constant MAX_ORACLE_AGE = 7 days;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L454-479)
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
```

**File:** evm/src/utils/SimplexPaymaster.sol (L563-583)
```text
    function _prefund(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        IERC20 token,
        uint256 tokenPrice,
        address prefunder_,
        uint256 maxCost
    )
        internal
        override
        returns (bool prefunded, uint256 prefundAmount, address prefunder, bytes memory prefundContext)
    {
        bytes calldata data = userOp.paymasterData();
        if (uint8(data[0]) != 0x02) {
            return super._prefund(userOp, userOpHash, token, tokenPrice, prefunder_, maxCost);
        }

        (, uint256 permitAmount, uint256 nonce, uint256 deadline, uint8 v, bytes32 r, bytes32 s) =
            _parsePermit2Data(data);
        prefundAmount = _erc20Cost(maxCost, userOp.maxFeePerGas(), tokenPrice);
        if (prefundAmount > permitAmount) revert InsufficientPermitAmount(permitAmount, prefundAmount);
```

**File:** evm/src/utils/SimplexPaymaster.sol (L653-676)
```text
    function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

        return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
    }

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

**File:** tesseract/messaging/evm/src/registry.rs (L90-102)
```rust
/// EVM chain IDs that Hyperbridge treats as L2 rollups of Ethereum. These are
/// the chains the collator-side fisherman task is required to monitor, and the
/// canonical source of truth used by the wrapper to enforce coverage of the
/// `[<chain>]` sections in the operator's tesseract toml.
///
/// Excludes Ethereum L1 itself, plus chains not finalized through Ethereum
/// (BSC, Gnosis, Polygon, Pharos), and Polkadot-finalized chains.
pub const SUPPORTED_L2_CHAIN_IDS_MAINNET: &[u64] = &[
	42161, // Arbitrum
	8453,  // Base
	10,    // Optimism
	1868,  // Soneium
];
```
