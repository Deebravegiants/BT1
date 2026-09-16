### Title
Missing Arbitrum sequencer-uptime check in `SimplexPaymaster._getOraclePrice` allows stale Chainlink prices to mis-price gas payments - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` is a permissionless ERC-4337 v0.8 paymaster deployed on multiple chains including Arbitrum (per `docs/content/developers/evm/simplex/configuration.mdx` line 81: "live on Ethereum, Arbitrum, Base, Polygon and BSC"). It prices ERC-20 gas payments using two Chainlink `AggregatorV3Interface` feeds read directly via `latestRoundData()` in `_getOraclePrice`, checking only for non-positive answers and heartbeat staleness (`block.timestamp - updatedAt > maxOracleAge`). It never checks Arbitrum's L2 sequencer-uptime feed, so it cannot detect the well-known Chainlink L2 gap where, immediately after a sequencer outage/restart, `latestRoundData()` can return a price that passes the heartbeat check yet does not reflect the true current market price. [1](#0-0) [2](#0-1) 

### Finding Description
`_getOraclePrice` is the sole price source feeding `_tokenPrice`, which determines how many ERC-20 tokens (USDC/USDT/etc.) a UserOperation's sender is charged for gas:
```solidity
function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
    (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();
    if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
    if (block.timestamp - updatedAt > maxOracleAge) {
        revert StaleOraclePrice(address(oracle), updatedAt);
    }
    ...
}
``` [3](#0-2) 

This is the exact bug class from the external report: on Arbitrum, Chainlink price feeds are updated by an off-chain reporting mechanism whose transactions are also sequenced by the Arbitrum sequencer. When the sequencer goes down and later comes back online, a backlog of feed updates can be delivered at once, or a feed's `updatedAt` may still satisfy the heartbeat window while the price itself is stale relative to true market conditions during the outage window. The standard mitigation — checking `FlagsInterface`/`L2SequencerUptimeFeed` for `startedAt`/`answer` and enforcing a grace period after the sequencer resumes — is completely absent from this contract, unlike the recommendation given for `ChainlinkAdapterOracle.sol`.

The function is reached from a fully unprivileged entry point: any UserOperation submitted through a bundler with `paymasterData` mode `0x00` or `0x02` invokes `_fetchDetails` → `_tokenPrice` → `_getOraclePrice`, with no privileged caller required: [4](#0-3) 

The computed `tokenPrice` directly sets `prefundAmount` pulled from the sender (mode 0x02 via Permit2, or mode 0x00 via a standing/one-shot permit approval) in `_prefund`: [5](#0-4) 

### Impact Explanation
If the Arbitrum sequencer stalls and Chainlink's native/USD or token/USD feed reports a price that is stale relative to the real market (but still within `maxOracleAge` of its last on-chain update timestamp), any unprivileged caller submitting a UserOperation through this paymaster can be charged an incorrect amount of the ERC-20 gas token:
- If the stale price undervalues the native asset relative to the token, the paymaster undercharges — an attacker can drain the paymaster's ability to recover its gas costs by triggering many UserOperations at the mispriced rate, resulting in a direct loss of protocol-held funds/treasury value once the surplus/markup and reimbursement model is skewed.
- Conversely, an overvalued native price relative to token overcharges legitimate solvers/users, taking excess funds from unsuspecting senders.

This is a concrete funds-loss vector reachable purely by submitting a transaction (UserOperation) — no privileged governance, admin, or off-chain relayer collusion is required — matching the "unbacked mint / theft of funds" severity bar. It is Medium severity because exploitation is bounded by the oracle's heartbeat window and depends on an actual sequencer outage occurring, and the ceiling on losses is bounded by `maxOracleAge` and the mode-0x00/0x02 permit amount caps.

### Likelihood Explanation
Likelihood is Medium: sequencer downtimes on Arbitrum are infrequent but have occurred historically, and this contract is explicitly documented as deployed live on Arbitrum. Any attacker (or even an honest actor unintentionally) submitting UserOperations during/immediately after a sequencer recovery window can trigger the mispricing without any special permissions, satisfying "reachable by a single submitted transaction."

### Recommendation
Add an Arbitrum L2 sequencer-uptime feed check (Chainlink `SequencerUptimeFeed`) before trusting `latestRoundData()` results in `_getOraclePrice`, following the same pattern recommended for `ChainlinkAdapterOracle.sol`:
- Query the sequencer uptime feed's `latestRoundData()`.
- Revert if `answer == 1` (sequencer is down) or if the time since the sequencer came back up (`block.timestamp - startedAt`) is less than a configured grace period (e.g., Chainlink's suggested 3600 seconds).
- Only proceed to trust the price/token oracles once the grace period has elapsed after sequencer restoration.

### Proof of Concept
1. `SimplexPaymaster` is deployed and configured on Arbitrum with a native/USD and token/USD Chainlink feed, `maxOracleAge` set to the feed's normal heartbeat (e.g., 3600s per `docs/content/developers/evm/simplex/configuration.mdx`/contract comments).
2. Arbitrum sequencer experiences an outage. Chainlink feed updates that would normally arrive during the outage are delayed and queued.
3. Once the sequencer resumes, a batch of prior price updates lands on-chain; during the window immediately following resumption, `latestRoundData().updatedAt` can still be within `maxOracleAge`, yet the reported price momentarily lags true market price (a documented Chainlink L2 risk).
4. Any address submits a UserOperation through a bundler with `paymasterData` mode `0x00` or `0x02`, referencing a registered/active token. `_fetchDetails` calls `_tokenPrice` → `_getOraclePrice`, which passes both the `answer <= 0` and staleness checks despite the underlying price being stale relative to the sequencer-down period.
5. `_prefund` (mode 0x02) or the base `PaymasterERC20._prefund` (mode 0x00) pulls `prefundAmount` computed from this mispriced `tokenPrice`, over- or under-charging the sender relative to the true gas cost, resulting in funds loss to either the sender or the paymaster's treasury depending on price direction. [6](#0-5) [7](#0-6)

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L516-556)
```text
    /// @dev Returns the token to charge and its price relative to native gas.
    ///
    ///      PaymasterERC20 computes `erc20Cost = weiCost * tokenPrice / 1e18`,
    ///      so tokenPrice must be token base units per wei, scaled by 1e18:
    ///        tokenPrice = (nativeUsd * 10^tokenDecimals) / tokenUsd
    ///      e.g. BNB at $600, USDC at $1 with 6 decimals: 0.001 BNB (1e15 wei)
    ///      should cost 0.60 USDC (600000 units), giving tokenPrice = 6e8, which
    ///      is exactly (600e8 * 1e6) / 1e8. Markup is applied on top.
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
        validationData = 0; // no time-range restriction

        if (mode == 0x02) {
            (,,, uint256 deadline,,,) = _parsePermit2Data(data);
            // Surfacing the permit deadline as validUntil lets bundlers drop
            // expiring ops instead of discovering it through a Permit2 revert.
            uint48 validUntil = deadline > type(uint48).max ? 0 : uint48(deadline);
            validationData = ERC4337Utils.packValidationData(true, 0, validUntil);
        }
    }
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

**File:** docs/content/developers/evm/simplex/configuration.mdx (L79-82)
```text
Solver selection requires each solver's EOA to be delegated to the `SolverAccount` contract. Simplex performs this automatically at startup via EIP-7702:

- **Primary path** — builds a no-op UserOperation with an attached EIP-7702 authorization and submits it through the configured bundler. When a paymaster is deployed on the chain — Circle Paymaster (USDC) preferred, then the `SimplexPaymaster` (USDC or USDT), live on Ethereum, Arbitrum, Base, Polygon and BSC — see [Mainnet Contract Addresses](/developers/evm/contract-addresses/mainnet) — and the solver holds at least one whole token of a supported stablecoin, the paymaster pays gas in that stablecoin so the solver never needs native gas for delegation. Tokens with EIP-2612 are authorized by permit; tokens without it (such as BSC stables) need a one-time funded `approve(Permit2, max)` from the solver EOA, after which every operation carries a per-op Permit2 signature and no native gas is ne ... (truncated)
- **Fallback** — if the bundler path fails or the chain has no paymaster, Simplex sends a direct type-0x04 delegation tx using the solver's native balance. On paymaster-less chains it also keeps the ERC-4337 EntryPoint deposit topped up to cover `targetGasUnits` (default 3,000,000) at the current gas price.
```
