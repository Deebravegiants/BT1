### Title
Shared native-asset oracle failure permanently DoSes gas-payment validation for every registered token in SimplexPaymaster - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster._tokenPrice` computes a token's gas price by querying **two** Chainlink feeds every time: the shared `nativeOracle` and the token-specific `cfg.tokenOracle`. `_getOraclePrice` unconditionally reverts with `InvalidOraclePrice` when a feed's `answer <= 0`, or `StaleOraclePrice` when it exceeds `maxOracleAge`. Because `nativeOracle` is shared across every registered token, a single failing feed (price hits zero/negative, or the feed stops updating) makes `_tokenPrice` revert for *all* tokens simultaneously, blocking every UserOperation that tries to pay gas through this paymaster, with no non-governance recovery path.

### Finding Description
`_tokenPrice` is invoked from `_fetchDetails`, which `PaymasterERC20._validatePaymasterUserOp` calls during ERC-4337 validation for every single UserOp that uses this paymaster: [1](#0-0) 

```solidity
function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
    uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
    uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
    return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
}
```

`_getOraclePrice` hard-reverts on any non-positive or stale answer: [2](#0-1) 

This is called from `_fetchDetails`, reached by `_validatePaymasterUserOp` for every submitted UserOp: [3](#0-2) [4](#0-3) 

`nativeOracle` is a single contract-wide value shared by every `TokenConfig` (there is exactly one `nativeOracle` slot, not one per token): [5](#0-4) 

If `nativeOracle` returns `answer <= 0` (a real Chainlink failure mode — e.g. LUNA/UST-style de-peg to zero, feed deprecation, or a sequencer-uptime-feed style zero return) or simply stops updating past `maxOracleAge`, **every** call to `_tokenPrice` for **every** registered token reverts. `getTokenPrice`, `estimateTokenCost`, and — critically — `_fetchDetails` (hence `_validatePaymasterUserOp`) all revert, so no UserOp can pay gas through this paymaster with any token, on any chain this paymaster instance serves.

Unlike the referenced `MarginAccount`, the only recovery mechanism here is fully centralized and cross-chain: the paymaster has "no privileged key" per its own docstring — every parameter change, including `UpdateParams` (which is the only way to replace `nativeOracle`) or `RegisterToken`, must arrive as a Hyperbridge governance POST message delivered by the single authorized relayer: [6](#0-5) [7](#0-6) 

This mirrors the root cause of the reported bug class exactly: a single external price feed reaching a degenerate value (`0`/negative) is treated as an unrecoverable `revert` condition inside a shared price-computation path that every unprivileged caller (any UserOp sender) must pass through, and the only fix requires a privileged, latency-bound governance round trip rather than an automatic or permissionless fallback/kill-switch specific to the failing feed.

### Impact Explanation
While the paymaster does not itself escrow user principal the way `MarginAccount` does, it *is* the sole gas-sponsorship mechanism for every token the operator supports on that chain. A stuck native-asset oracle:
- Reverts `_validatePaymasterUserOp` for all UserOps across all registered tokens, denying service to every user relying on gas abstraction via this paymaster.
- Also breaks `swapAndDeposit` (which calls the same `_getOraclePrice` for `nativeOracle`), preventing the treasury from recycling collected token fees into native EntryPoint stake, and `getTokenPrice`/`estimateTokenCost` used by the SDK/bundlers for fee quoting.
- Cannot be repaired without a full cross-chain governance flow (Hyperbridge dispatch → consensus proof → relayer delivery → `onAccept` → `UpdateParams`), which is far slower than a local emergency parameter update, and the paymaster explicitly has no privileged fallback key — losing the single relayer key "loses governance for good."

This satisfies "a route unable to deliver messages"/service-availability class of Medium impact: a shared oracle degenerate value freezes gas-sponsored transaction flow for every supported asset until a slow, privileged, cross-chain fix lands.

### Likelihood Explanation
Chainlink feeds returning `0` or going stale is a documented, previously-observed failure mode (e.g., during extreme depegs or feed deprecations), and native-asset (ETH/BNB/etc.) feeds are just as susceptible as any other feed. Because `nativeOracle` is a single point of failure shared by every token, the probability of the shared feed failing is no lower than for any individual token feed, yet its blast radius covers the entire paymaster rather than one token. No attacker action is required — the trigger is purely a degenerate oracle answer, reachable passively by any oracle malfunction and observable/exploitable via ordinary UserOp submission (fully unprivileged).

### Recommendation
- Do not let a non-positive/stale `nativeOracle` (or any single feed) permanently DoS all tokens. Consider: (a) a fallback/secondary oracle for the native asset, (b) per-token circuit breaking so a broken oracle only disables that specific token rather than reverting `_tokenPrice` globally, or (c) allowing a bounded, permissionless "last known good price" fallback with a safety margin instead of an unconditional revert.
- Add a lower-latency recovery path (e.g., an emergency pause/kill switch for a specific feed) that does not require the full Hyperbridge governance round trip, since the current design's only remedy for a broken oracle is an `UpdateParams`/`RegisterToken` governance message routed through cross-chain consensus and a single relayer.
- Emit a distinguishable error/event when a specific token's oracle fails vs. when the shared native oracle fails, so operators can triage and route around single-feed outages faster.

### Proof of Concept
1. Chainlink's `nativeOracle` feed for the paymaster's native asset (e.g., BNB/USD) returns `answer == 0` (or `<= 0`) from `latestRoundData()`, or simply stops updating past `maxOracleAge` (a real-world feed failure/deprecation).
2. Any user submits a normal UserOp naming this paymaster and any registered ERC-20 token in `paymasterData`.
3. The bundler/EntryPoint calls `validatePaymasterUserOp` → `_validatePaymasterUserOp` → `super._validatePaymasterUserOp` → `_fetchDetails(userOp, ...)`.
4. `_fetchDetails` calls `_tokenPrice(cfg)` → `_getOraclePrice(nativeOracle, nativeOracleDecimals)`, which reverts with `InvalidOraclePrice(nativeOracle, 0)` (or `StaleOraclePrice`).
5. Validation reverts for this UserOp, and reverts identically for **every** UserOp naming **any** registered token, because `nativeOracle` is queried unconditionally before the token-specific feed. Repeat with a second, unrelated token to confirm the DoS is global, not scoped to the token whose price failed.
6. No entry point in the contract lets any account restore service except a Hyperbridge governance `UpdateParams`/`RegisterToken` message delivered by the single authorized relayer (`onAccept`), confirming there is no unprivileged or fast recovery path.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L196-202)
```text
    AggregatorV3Interface public nativeOracle;
    uint8 public nativeOracleDecimals;
    uint256 public maxOracleAge;
    uint256 public markupBps;
    address public treasury;

    mapping(address => TokenConfig) public tokenConfigs;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L309-344)
```text
    /// @dev Handles governance requests delivered by the local host. The first
    ///      byte of the request body encodes the `RequestKind`; only requests
    ///      originating from Hyperbridge itself, submitted by the authorised
    ///      relayer, are accepted.
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) {
            revert UnauthorizedCall();
        }

        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        bytes calldata payload = incoming.request.body[1:];

        if (kind == RequestKind.UpgradeContract) {
            (address newImpl, bytes memory initData) = abi.decode(payload, (address, bytes));
            ERC1967Utils.upgradeToAndCall(newImpl, initData);
        } else if (kind == RequestKind.UpdateParams) {
            _setParams(abi.decode(payload, (Params)));
        } else if (kind == RequestKind.RegisterToken) {
            (address token, address oracle) = abi.decode(payload, (address, address));
            _registerToken(token, AggregatorV3Interface(oracle));
        } else if (kind == RequestKind.DeactivateToken) {
            _deactivateToken(abi.decode(payload, (address)));
        } else if (kind == RequestKind.WithdrawAssets) {
            (address token, uint256 amount) = abi.decode(payload, (address, uint256));
            _withdrawAssets(token, amount);
        } else if (kind == RequestKind.UnlockStake) {
            entryPoint().unlockStake();
        } else if (kind == RequestKind.WithdrawStake) {
            entryPoint().withdrawStake(payable(treasury));
        } else if (kind == RequestKind.SetRelayer) {
            address newRelayer = abi.decode(payload, (address));
            if (newRelayer == address(0)) revert ZeroAddress();
            _setRelayer(newRelayer);
        }
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L357-383)
```text
    /// @dev Validates and applies pricing/treasury parameters, re-caching the
    ///      native oracle decimals.
    function _setParams(Params memory p) internal {
        if (address(p.nativeOracle) == address(0)) revert ZeroAddress();
        if (p.treasury == address(0)) revert ZeroAddress();
        if (p.markupBps > MAX_MARKUP_BPS) revert InvalidMarkup(p.markupBps);
        if (p.maxOracleAge == 0 || p.maxOracleAge > MAX_ORACLE_AGE) revert InvalidOracleAge(p.maxOracleAge);
        if (p.swapSlippageBps > MAX_SWAP_SLIPPAGE_BPS) revert InvalidSlippage(p.swapSlippageBps);

        emit ParamsUpdated(
            Params({
                nativeOracle: nativeOracle,
                markupBps: markupBps,
                treasury: treasury,
                maxOracleAge: maxOracleAge,
                swapSlippageBps: swapSlippageBps
            }),
            p
        );

        nativeOracle = p.nativeOracle;
        nativeOracleDecimals = p.nativeOracle.decimals();
        markupBps = p.markupBps;
        treasury = p.treasury;
        maxOracleAge = p.maxOracleAge;
        swapSlippageBps = p.swapSlippageBps;
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L492-514)
```text
    function _validatePaymasterUserOp(PackedUserOperation calldata userOp, bytes32 userOpHash, uint256 maxCost)
        internal
        override
        returns (bytes memory context, uint256 validationData)
    {
        uint256 postOpGasLimit = userOp.paymasterPostOpGasLimit();
        if (postOpGasLimit > MAX_POST_OP_GAS_LIMIT || postOpGasLimit < MIN_POST_OP_GAS_LIMIT) {
            revert InvalidPostOpGasLimit(postOpGasLimit, MIN_POST_OP_GAS_LIMIT, MAX_POST_OP_GAS_LIMIT);
        }

        bytes calldata data = userOp.paymasterData();
        if (data.length == 0) revert InvalidPaymasterData(0);
        if (uint8(data[0]) == 0x00) {
            if (data.length < 21) revert InvalidPaymasterData(data.length);
            address tokenAddr = address(bytes20(data[1:21]));
            TokenConfig memory cfg = tokenConfigs[tokenAddr];
            if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(tokenAddr);
            if (!cfg.active) revert TokenNotActive(tokenAddr);
            _executePermit(userOp);
        }

        return super._validatePaymasterUserOp(userOp, userOpHash, maxCost);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L524-556)
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

        if (mode == 0x02) {
            (,,, uint256 deadline,,,) = _parsePermit2Data(data);
            // Surfacing the permit deadline as validUntil lets bundlers drop
            // expiring ops instead of discovering it through a Permit2 revert.
            uint48 validUntil = deadline > type(uint48).max ? 0 : uint48(deadline);
            validationData = ERC4337Utils.packValidationData(true, 0, validUntil);
        }
    }
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
