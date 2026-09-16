## Analog Found [1](#0-0) 

### Title
Missing Chainlink price bounds/deviation check allows theft of paymaster deposit during depeg or oracle circuit-breaker events - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` is a permissionless ERC-4337 paymaster that lets any unprivileged UserOp sender (including intent solvers, per the `sdk/packages/simplex` filler tooling) pay gas fees in ERC-20 stablecoins, converted to native currency using two Chainlink feeds. The oracle-reading function only checks for staleness and non-positive answers — it never validates the returned price against the feed's known min/max circuit-breaker bounds, mirroring exactly the reported LibUbiquityPool.sol issue class.

### Finding Description
`_getOraclePrice` fetches `latestRoundData()` and only guards against `answer <= 0` and staleness via `maxOracleAge`: [2](#0-1) 

This price feeds directly into `_tokenPrice`, which computes how much of a registered ERC-20 (e.g. USDC/USDT) is owed for gas sponsored through the EntryPoint: [3](#0-2) 

Chainlink aggregators are documented to return their configured `minAnswer`/`maxAnswer` bound instead of reverting when the true price moves outside that range (e.g. during a stablecoin depeg or a native-asset flash crash). Because `SimplexPaymaster` never compares the returned answer against any expected band or deviation threshold, it will silently accept the clamped border price as truth. The same unguarded price also feeds `swapAndDeposit`'s `expectedWei` computation used to size `amountOutMin` for a live token→native swap: [4](#0-3) 

The contract's own comment set only defends against a "malicious oracle" via capping the solver's Permit2/permit residual allowance — it does not defend against a live, legitimate-but-bounded Chainlink answer during a market dislocation: [5](#0-4) 

### Impact Explanation
If a registered stablecoin depegs downward (e.g. USDC-style event) while its Chainlink feed clamps at its `minAnswer` bound (typically near $1), `_tokenPrice` will keep charging UserOps as if the token is still worth par. Any unprivileged actor holding the devalued token can then repeatedly submit sponsored UserOps, paying gas with tokens priced above their real market value, draining the paymaster's EntryPoint deposit (funded by the treasury) at a favorable, stale exchange rate. Symmetrically, a spike in the native asset's price hitting the feed's `maxAnswer` bound would let a user pay in nearly worthless token amounts for gas actually worth much more, again extracting value from the paymaster. This is a direct, permissionless drain of pooled deposit funds — not merely a display/accounting bug.

### Likelihood Explanation
Reachability requires no privileged role: any address that can submit an ERC-4337 UserOp using `SimplexPaymaster`'s mode 0x00/0x02 paymasterData can trigger `_tokenPrice`/`_getOraclePrice` on every sponsored operation. Chainlink circuit-breaker clamping during depegs and flash crashes is a documented, recurring real-world event class (e.g., USDC March 2023), making exploitation realistic whenever a registered token or the native asset undergoes a sharp deviation while the feed is still "fresh" per the staleness check.

### Recommendation
Extend `_getOraclePrice` to reject (or degrade gracefully, e.g. pause the affected token) when the returned `answer` equals or is within an epsilon of the aggregator's configured `minAnswer`/`maxAnswer`, or alternatively cross-check against a secondary source (TWAP/Uniswap) with a maximum allowed deviation before accepting the Chainlink price, consistent with the mitigation referenced in the source report.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L53-93)
```text
/// @title  SimplexPaymaster
/// @author Polytope Labs
/// @notice Fully onchain, permissionless ERC-4337 v0.8 paymaster that accepts
///         ERC-20 stablecoins (USDC, USDT, or any token with a Chainlink feed)
///         for gas payment. Deployed behind an ERC1967Proxy and administered
///         exclusively through Hyperbridge governance.
///
/// Modes (byte 0 of paymasterData):
///   0x00  PERMIT  — EIP-2612 permit signature included; the permit is executed
///                    during validation so the subsequent prefund transferFrom
///                    succeeds without a prior onchain approval.
///   0x02  PERMIT2 — Permit2 SignatureTransfer signature included; the prefund
///                    is pulled through Permit2.permitTransferFrom, so the token
///                    only needs a one-time approval to Permit2 (the path for
///                    tokens without permit support, e.g. BSC stablecoins).
///   Any other mode byte, including the retired 0x01 that spent a standing
///   allowance to this contract, is refused with {InvalidMode}.
///
/// paymasterData encoding:
///   Mode 0x00 (permit):
///     abi.encodePacked(uint8(0), address(token), uint256(permitAmount),
///                      uint256(deadline), uint8(v), bytes32(r), bytes32(s))
///   Mode 0x02 (permit2):
///     abi.encodePacked(uint8(2), address(token), uint256(permitAmount),
///                      uint256(nonce), uint256(deadline), uint8(v), bytes32(r), bytes32(s))
///     the signed spender is this paymaster.
///
/// Price conversion uses two Chainlink feeds: token/USD and nativeAsset/USD.
/// The markup surplus accumulates in the contract and is withdrawable to the
/// treasury; unused gas is refunded to the sender by PaymasterERC20._postOp.
///
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

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
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
