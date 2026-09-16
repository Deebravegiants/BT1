Confirmed: `SimplexPaymaster._getOraclePrice()` validates only non-positive answers and staleness, never the Chainlink `minAnswer`/`maxAnswer` clamp, and its output feeds directly into `_tokenPrice()` used by the permissionless `_fetchDetails`/`_prefund` path that any UserOperation sender can trigger by picking a registered token.

### Title
ChainlinkOracle-style price clamp bypass in `SimplexPaymaster._getOraclePrice()` lets any user underpay gas with a depegging token - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster._getOraclePrice()` reads Chainlink's `latestRoundData()` and only rejects `answer <= 0` and stale updates, exactly mirroring the audited `ChainlinkOracle::getPriceInEth()` bug class: it never checks whether the aggregator's `answer` equals the feed's `minAnswer`/`maxAnswer`, so a crashing/depegging registered token continues to be priced at the clamped floor instead of its real market value. [1](#0-0) 

### Finding Description
`_getOraclePrice` is the sole price source feeding `_tokenPrice(cfg)`, which computes `tokenPrice = nativeUsd * 10^decimals * (1+markup) / tokenUsd` used to charge gas fees in ERC-20 tokens. [2](#0-1) 
This value is returned from `_fetchDetails`, invoked for every permissionless UserOperation that selects a registered token via `paymasterData`, with no restriction on who can submit such an op. [3](#0-2) 
`tokenPrice` is then used in `_prefund`/`_erc20Cost` to determine how many token units are pulled from the sender to cover gas. [4](#0-3) 

If a registered token's Chainlink feed hits its aggregator-configured `minAnswer` (e.g., a stablecoin depegging sharply below $1), `latestRoundData()` keeps reporting the clamped floor price instead of the real, lower price. Since `tokenUsd` sits in the denominator of `_tokenPrice`, an artificially high (clamped) `tokenUsd` produces an artificially *low* `tokenPrice`, meaning the paymaster charges the sender fewer token units than the token's real worth requires to cover the actual gas cost. Any unprivileged UserOperation sender holding the depegged token can submit ops, pay in that near-worthless token at the stale clamped rate, and receive full native-gas-value sponsorship from the paymaster, draining the paymaster's EntryPoint deposit/treasury value. The contract's own documentation only discusses bounding exposure "even against a malicious oracle" via the small permit amounts, but that mitigation limits attacker profit per operation—not the underlying flawed pricing—and provides no protection against a legitimately malfunctioning (clamped) but non-malicious feed, nor against repeated exploitation across many operations, or the reciprocal case where the native-asset oracle clamps. [5](#0-4) 

### Impact Explanation
This is a fund-loss issue: the paymaster's treasury-controlled EntryPoint deposit (funded by governance and fee recycling) subsidizes gas for tokens that are worth far less than the price the contract uses, so real ETH-backed value leaks to any op sender who can source or acquire the affected token cheaply after depeg. Because gas payment paths run without any circuit breaker on price bounds, this is a systemic, permanent-loss risk for any registered token that experiences a large de-peg or crash event, matching Medium severity per the referenced Chainlink `minAnswer`/`maxAnswer` bug class.

### Likelihood Explanation
Likelihood is tied to external market events (a registered token's price crashing through the aggregator's configured bounds), which is realistic for stablecoins historically (e.g., USDC/USDT depeg events) — a class of event Chainlink explicitly documents and recommends guarding against. No special privilege is needed to trigger the exploit path beyond holding/acquiring the depegged token and submitting a normal UserOperation.

### Recommendation
In `_getOraclePrice`, fetch the aggregator's configured `minAnswer`/`maxAnswer` (via `aggregator()` on the proxy or a stored per-token config) and revert (or freeze the affected token) if the returned `answer` is at or near those bounds, consistent with Chainlink's documented guidance already cited in the analogous report.

### Proof of Concept
1. Governance registers `tokenX` (a stablecoin) via `RegisterToken` with its Chainlink `token/USD` feed.
2. `tokenX` depegs catastrophically (real price $0.10) and its Chainlink aggregator's `minAnswer` clamp holds `latestRoundData().answer` at $0.95.
3. Attacker acquires cheap `tokenX` on the open market, then submits a UserOperation with `paymasterData` mode `0x00`/`0x02` selecting `tokenX`.
4. `_fetchDetails` → `_tokenPrice` computes `tokenPrice` using the clamped $0.95 instead of the real $0.10 — under-charging the attacker roughly 9.5x relative to the token's true value.
5. `_prefund` pulls the under-priced amount of near-worthless `tokenX`; `PaymasterERC20._postOp` still sponsors the full real gas cost from the EntryPoint deposit, resulting in a net value drain to the attacker. [6](#0-5)

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

**File:** evm/src/utils/SimplexPaymaster.sol (L524-547)
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
        validationData = 0; // no time-range restriction
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
