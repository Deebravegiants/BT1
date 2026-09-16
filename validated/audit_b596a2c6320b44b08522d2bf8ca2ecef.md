## Analog Found

### Title
Unhandled Chainlink oracle revert in `SimplexPaymaster` bricks ERC-20 gas payment for a token, blocking dispatch by unprivileged UserOp submitters - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` is a permissionless ERC-4337 paymaster that lets any unprivileged submitter pay for the gas of dispatching a Hyperbridge message with a registered ERC-20 token, using Chainlink price feeds to compute the token price. The price-fetch helper `_getOraclePrice` calls `oracle.latestRoundData()` directly, with no `try/catch`, exactly the pattern flagged in the referenced report. If Chainlink pauses, deprecates, or otherwise blocks the underlying feed so the call reverts, every validation of a UserOp using that token reverts too, denying that gas-payment route to all unprivileged users until governance intervenes.

### Finding Description
`_getOraclePrice` fetches the price straight from the Chainlink aggregator with no fallback: [1](#0-0) 

This is called unconditionally from `_tokenPrice`, which computes the ERC-20/native gas conversion rate for both the native and token oracles: [2](#0-1) 

`_tokenPrice` is invoked from `_fetchDetails`, the ERC-4337 validation hook that runs for every incoming `PackedUserOperation` submitted by any unprivileged party attempting to pay gas in a registered token: [3](#0-2) 

If `oracle.latestRoundData()` reverts (Chainlink access blocked/feed deprecated), this bubbles all the way up through `_tokenPrice` → `_fetchDetails` → `_validatePaymasterUserOp`, causing every UserOp that tries to pay gas with that token to revert — exactly the same "unhandled external price-feed revert breaks a core, reachable entry point" pattern as the referenced report's `Oracle.viewPrice`/`getPrice`.

The contract's own comment acknowledges this failure mode and treats re-registration as the recovery path, i.e., there is no automatic fallback — recovery requires a governance action delivered through the host's `onAccept`: [4](#0-3) 

### Impact Explanation
While the underlying Hyperbridge `dispatch()` path itself is unaffected (users can still pay fees directly in the fee token or native token through `EvmHost`), any unprivileged user or bundler who wants to submit a message-dispatch transaction sponsored by this paymaster and paid for in the affected ERC-20 token is completely blocked from doing so until Hyperbridge governance re-registers a working oracle for that token. This is a concrete "route unable to deliver messages" scenario for that specific payment path, since a bundler must simulate/validate the UserOp before including it, and validation will always revert while the feed is blocked.

### Likelihood Explanation
Chainlink feed access being blocked or a feed being deprecated/frozen is a documented external risk (as referenced in the OpenZeppelin blog cited by the original report) and has occurred historically for some feeds. Any unprivileged actor attempting to use the affected token to pay gas triggers the revert path — no special privileges or preconditions are required beyond selecting that token in `paymasterData`.

### Recommendation
Wrap the Chainlink call in `_getOraclePrice` in a `try/catch`, and on failure either (a) reject only that specific token's payment mode gracefully with a clear custom error rather than an opaque low-level revert, and/or (b) support an admin-settable fallback/fixed price or a secondary oracle so a blocked feed does not fully brick the token as a gas-payment method while governance recovers, reducing the window where legitimate users relying on that token cannot dispatch operations.

### Proof of Concept
1. Governance registers token `T` with Chainlink oracle `O` via `_registerToken` (`SimplexPaymaster.sol:387-404`).
2. Chainlink flags or pauses `O` so `O.latestRoundData()` reverts (or the feed contract self-destructs/is deprecated).
3. An unprivileged user submits a `PackedUserOperation` with `paymasterData` mode `0x00`/`0x02` selecting token `T`.
4. The bundler's simulation (and any live inclusion attempt) calls `_validatePaymasterUserOp` → `_fetchDetails` → `_tokenPrice` → `_getOraclePrice(cfg.tokenOracle, ...)`, which reverts because `O.latestRoundData()` reverts.
5. Every UserOp attempting to pay gas in token `T` reverts until Hyperbridge governance calls `_registerToken` again with a working oracle, per the "recovery path" comment at `SimplexPaymaster.sol:386-387`.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L385-387)
```text
    /// @dev Registers or updates a supported ERC-20 token with its token/USD feed.
    ///      Re-registering is also the recovery path for a misbehaving oracle.
    function _registerToken(address token, AggregatorV3Interface oracle) internal {
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
