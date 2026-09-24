Based on the codebase investigation: alt.fun's contracts contain no `payable`/`receive()`/`fallback()` at all in `packages/contracts/src` — the protocol is entirely USDC/LT/Token/LP-token based, so the exact "stuck ETH via a bare `receive()`" bug class from the Napier `SFrxETHAdapter` report does not literally exist here.

However, the same root cause — a value-holding contract that can accept inbound transfers but exposes **no withdrawal/rescue path whatsoever** — reproduces in `LPLock.sol`. Unlike `FeeVault` (which has `sweepDonations()`) or `Bonding` (which actively skims/burns/sweeps stray token and LT donations during graduation via `_sweepLTToOwner` and the `_seedUniswapV2Direct` skim-and-burn pattern), `LPLock` has zero recovery mechanism for anything beyond the exact amount recorded by `recordLock`. [1](#0-0) 

### Title
Any ERC20 (including stray LP tokens) sent directly to LPLock is permanently unrecoverable — no rescue/withdraw path exists - ([File: packages/contracts/src/LPLock.sol])

### Summary
`LPLock` is a UUPS contract whose sole storage-mutating entrypoint is `recordLock`, which is gated to allowlisted lockers and can only be called once per token (`AlreadyLocked` guard). It has **no** `sweep`, `withdraw`, `rescue`, or owner-controlled recovery function of any kind. Any ERC20 token — the graduated HyperSwap LP token itself, the launched `Token`, the LT, or an unrelated token — transferred to the `LPLock` address by any unprivileged wallet is permanently and irrecoverably locked, exactly mirroring the reported bug class of a `payable` contract accepting funds with no corresponding withdrawal mechanism.

### Finding Description
`LPLock.recordLock` only checks that the contract's balance of the specific `lpPair` token is `>= amount` before recording the lock; it never sweeps or reconciles any excess balance, and no other function in the contract can move tokens out. [2](#0-1) 

This is a deliberate, acknowledged design choice — the codebase's own comments state "LPLock has no rescue path in v1, so anything sent there is permanently stuck" — and other contracts in the same system (`Bonding`, `FeeVault`) explicitly route donations *away* from `LPLock` for this exact reason: [3](#0-2) [4](#0-3) 

Any unrelated wallet can trivially strand value at `LPLock` two ways: (1) a plain `IERC20.transfer` of the launched `Token`, the LT, USDC, or any other ERC20 directly to the `LPLock` address, mistaking it for a claim/vault address (the exact same user-mistake scenario as the original report's "mistakenly sent ETH"); or (2) an attacker who independently provides liquidity to the same HyperSwap V2 pair and calls `pair.mint(lpLockAddress)` directly, minting extra LP tokens to `LPLock`'s balance outside the `recordLock` accounting — that excess is never reconciled or recoverable, since `recordLock`'s one-shot guard (`lockedAt != 0`) prevents any subsequent call from ever touching that token's lock record again.

### Impact Explanation
Funds sent to `LPLock` — by mistake, by griefing, or via an attacker minting excess LP directly to it — are permanently and irrecoverably frozen with no on-chain or owner-privileged path to reclaim them, satisfying the "permanent freezing of funds" impact bar. This is Medium severity: it requires an external actor's mistaken or excess transfer (not a direct protocol insolvency), matching the severity of the original report.

### Likelihood Explanation
Likelihood is non-trivial: `LPLock`'s address is publicly known (it is the recipient of every graduation's locked LP, emitted in `TokenGraduated`/`LPLocked` events), making it a plausible target for mistaken transfers by users unfamiliar with the contract's role, and a low-cost target for a griefer to mint stray LP into to permanently waste value.

### Recommendation
Add an owner-only `sweep(address token, uint256 amount, address to)` function to `LPLock` (mirroring `FeeVault.sweepDonations`) that only allows sweeping token balances in excess of what is recorded by `recordLock` for that token's `lpPair`, so the intentionally-locked LP allocation can never be touched while stray/excess transfers can be recovered.

### Proof of Concept
1. `Bonding.finalizeGraduation` graduates `tokenA`, minting `liquidity` LP tokens to `LPLock` and calling `recordLock(tokenA, pairA, liquidity)`.
2. A stranger, having independently added liquidity to `pairA` off-protocol (e.g., by directly calling `pairA.mint(lpLockAddress)` after transferring extra TOKEN/LT to `pairA`), causes `IERC20(pairA).balanceOf(lpLockAddress)` to exceed the recorded `amount`.
3. Because `recordLock(tokenA, ...)` has already been called once, `AlreadyLocked` blocks any further recording of the excess for `tokenA`, and no function exists to withdraw, sweep, or otherwise account for the extra LP balance — it sits at `LPLock` forever.
4. Separately, any wallet can call `IERC20(anyToken).transfer(lpLockAddress, amount)` at any time (even for a token never associated with any pair) and that balance is permanently unreachable, as `LPLock` exposes no function referencing `anyToken` at all.

### Citations

**File:** packages/contracts/src/LPLock.sol (L8-18)
```text
/// @title LPLock
/// @notice Locks LP tokens from graduated tokens. No withdraw in v1.
/// @dev UUPS-upgradeable to support v2 `migrateLT` functionality.
///      Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
///
///      Storage uses ERC-7201 namespaced layout (no `__gap` needed). All
///      mutable state lives in `LPLockStorage` at `_LP_LOCK_STORAGE_LOCATION`.
```

**File:** packages/contracts/src/LPLock.sol (L69-85)
```text
    /// @notice Record an LP lock. LP tokens must already sit at this address.
    function recordLock(
        address token,
        address lpPair,
        uint256 amount
    ) external {
        LPLockStorage storage $ = _s();
        if (!$.isLocker[msg.sender]) revert NotAuthorized();
        if (lpPair == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        // `lockedAt` is the one-shot sentinel: it is always set to a non-zero
        // timestamp on the first lock, so the guard holds for any `amount`.
        if ($.locks[token].lockedAt != 0) revert AlreadyLocked();
        if (IERC20(lpPair).balanceOf(address(this)) < amount) revert InsufficientLPBalance();
        $.locks[token] = LockInfo({lpPair: lpPair, amount: amount, lockedAt: block.timestamp});
        emit LPLocked(token, lpPair, amount);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1209-1215)
```text
        // Regime 2 — pull any donation pre-seed into this contract so it
        // doesn't pollute the post-swap ratio. Routed to `address(this)`
        // (NOT `lpLock`) so donated TOKEN can be burned and donated LT
        // can be swept to the owner via `_sweepLTToOwner` — `LPLock` has
        // no rescue path, so anything sent there is permanently stuck.
        // No-op on a freshly-created pair (balance == reserves == 0).
        IUniswapV2Pair(pair).skim(address(this));
```

**File:** packages/contracts/src/FeeVault.sol (L147-160)
```text
    /// @notice Sweep unbacked USDC (donations) to `feeTo`. Required because
    ///         direct USDC transfers would otherwise inflate `balanceOf` above
    ///         the accrual tally and silently mask the `accrue` underfund
    ///         check. Permissionless — funds always go to the admin-set `feeTo`.
    function sweepDonations() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        uint256 backed = $.totalAccruedCreator + $.protocolBalance;
        uint256 balance = $.usdc.balanceOf(address(this));
        if (balance <= backed) revert NothingToClaim();
        amount = balance - backed;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit DonationsSwept(feeTo_, amount);
    }
```
