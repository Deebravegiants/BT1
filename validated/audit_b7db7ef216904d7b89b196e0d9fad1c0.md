### Title
FeeVault becoming blacklisted permanently freezes every creator's and the protocol's accrued USDC fees - (File: packages/contracts/src/FeeVault.sol)

### Summary
`FeeVault` is the single, permanent, shared collection point for every creator's and the protocol's USDC trading fees across all tokens launched on alt.fun [1](#0-0) . Exactly like the reported `HGTRemote` pattern — a single shared contract address whose USDC-level blacklisting bricks value for many unrelated parties, not just one bad actor — a Circle-level blacklist action against the `FeeVault` contract address would permanently freeze all pooled creator and protocol USDC balances with no recovery path, because every outbound path is a `safeTransfer` *from* that one address.

### Finding Description
`Zap` forwards every buy/sell fee in USDC into `FeeVault` and calls `accrue`, which only updates internal accounting (`creatorBalance`, `protocolBalance`, lifetime counters) [2](#0-1) . The USDC itself physically sits in the `FeeVault` contract's own balance. All three withdrawal paths — `claim()`, `claimProtocol()`, and `sweepDonations()` — call `$.usdc.safeTransfer(...)` where the implicit `from` is `address(this)` (the vault) [3](#0-2) .

USDC's blacklist (`isBlacklisted`) is enforced by the token contract itself and blocks a transfer if *either* the sender or receiver is blacklisted — this is exactly the mechanism referenced in the external report and mirrored in this repo's own `forge-std` `assumeNotBlacklisted` helper, which checks USDC's `isBlacklisted(address)` selector `0xfe575a87` [4](#0-3) . If the `FeeVault` address itself is ever placed on that blacklist (e.g., mistakenly flagged, or targeted because it is a large aggregation point routing funds from many wallets), every `safeTransfer` *from* it reverts unconditionally, regardless of who the recipient is.

Unlike `feeTo`, which the owner can rotate away from a blacklisted recipient via `setFeeTo` [5](#0-4) , there is no mechanism to rotate the *sender* — the USDC balance is physically locked inside the blacklisted contract address. Being UUPS-upgradeable does not help: an upgrade can change logic but cannot bypass USDC's on-chain check against the `FeeVault` contract's own address as `msg.sender`/`from` in `transfer`/`transferFrom`. The documented mitigation for "Router swapability" only lets a *new* depositor (Zap) be whitelisted for *future* accruals into a *new* `FeeVault`; it explicitly leaves existing balances untouched in the old vault [6](#0-5)  — which is precisely the balance that becomes permanently stranded if the old vault is blacklisted.

### Impact Explanation
This satisfies "FeeVault insolvency" directly: every creator across every token ever launched, plus the protocol's own `feeTo`, has their entire accrued (but unclaimed) USDC fee balance permanently frozen the moment `FeeVault`'s address is blacklisted by USDC. `totalAccruedCreator` and `protocolBalance` become unrecoverable — `claim()`, `claimProtocol()`, and `sweepDonations()` all revert forever [3](#0-2) . No owner action, upgrade, or governance call can move USDC *out of* a blacklisted address — only Circle can reverse the blacklist, which is outside the protocol's control (Medium severity, matching the source report's rating for the analogous `HGTRemote` bridge-bricking scenario).

### Likelihood Explanation
This requires an external, non-protocol-controlled event (Circle blacklisting the vault address), so likelihood is low-probability but plausible over the contract's lifetime — the same likelihood profile as the original `HGTRemote` finding, which was also accepted at Medium severity despite requiring an external blacklist action. `FeeVault` is a natural target because it continuously aggregates USDC inflows from an unbounded set of buyers/sellers across every token, making it exactly the kind of "large aggregator" address automated compliance screening tools flag.

### Recommendation
Add an owner-gated (or timelocked) `rescueByMigration` path that, upon detecting/anticipating blacklist risk, allows funds to be pre-emptively migrated to a fresh `FeeVault` *before* a blacklist event (this cannot help after the fact, so the real mitigation is operational: monitor the vault's blacklist status and migrate depositors preemptively). Consider allowing `claim()`/`claimProtocol()` to accept a caller-supplied non-blacklisted recipient address instead of hardcoding `msg.sender`/`feeTo`, which at least protects individual creators if only their own personal recipient — not the vault itself — gets blacklisted, and reduces (though does not eliminate) the surface described above.

### Proof of Concept
1. `Zap.buy`/`Zap.sell` fees accrue over time into `FeeVault` via `accrue`, with real USDC balance held at `address(FeeVault)` [2](#0-1) .
2. Circle blacklists `address(FeeVault)` on USDC (out-of-protocol event, as in the source report's HGTRemote scenario).
3. Any creator calls `claim()` → `$.usdc.safeTransfer(msg.sender, amount)` reverts because the `from` (`FeeVault`) is blacklisted [7](#0-6) .
4. `claimProtocol()` and `sweepDonations()` revert identically [8](#0-7) .
5. Deploying a new `FeeVault` and whitelisting it as `Zap`'s depositor only routes *future* fees there; the balance already in the old, now-blacklisted `FeeVault` remains permanently unclaimable by any creator or the protocol.

### Citations

**File:** packages/contracts/src/FeeVault.sol (L31-45)
```text
    struct FeeVaultStorage {
        IERC20 usdc;
        /// @notice Protocol fee recipient. Receives `claimProtocol()` payout.
        address feeTo;
        EnumerableSet.AddressSet depositors;
        mapping(address creator => uint256) creatorBalance;
        uint256 protocolBalance;
        /// @notice Lifetime gross creator USDC accrued (never decreases).
        mapping(address creator => uint256) lifetimeCreatorEarned;
        uint256 lifetimeProtocolEarned;
        /// @notice Running sum of unclaimed creator balances. Lets `accrue`
        ///         do its underfund check in O(1) without iterating the
        ///         creator mapping.
        uint256 totalAccruedCreator;
    }
```

**File:** packages/contracts/src/FeeVault.sol (L101-123)
```text
    function accrue(
        address token,
        address creator,
        uint256 creatorAmount,
        uint256 protocolAmount,
        bool isBuy
    ) external onlyDepositor {
        FeeVaultStorage storage $ = _s();
        if (creatorAmount > 0) {
            if (creator == address(0)) revert ZeroAddress();
            $.creatorBalance[creator] += creatorAmount;
            $.totalAccruedCreator += creatorAmount;
            $.lifetimeCreatorEarned[creator] += creatorAmount;
        }
        if (protocolAmount > 0) {
            $.protocolBalance += protocolAmount;
            $.lifetimeProtocolEarned += protocolAmount;
        }
        if ($.usdc.balanceOf(address(this)) < $.totalAccruedCreator + $.protocolBalance) {
            revert UnderfundedAccrual();
        }
        emit FeeAccrued(token, creator, creatorAmount, protocolAmount, isBuy);
    }
```

**File:** packages/contracts/src/FeeVault.sol (L127-160)
```text
    function claim() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        amount = $.creatorBalance[msg.sender];
        if (amount == 0) revert NothingToClaim();
        $.creatorBalance[msg.sender] = 0;
        $.totalAccruedCreator -= amount;
        $.usdc.safeTransfer(msg.sender, amount);
        emit CreatorFeesClaimed(msg.sender, amount);
    }

    function claimProtocol() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        amount = $.protocolBalance;
        if (amount == 0) revert NothingToClaim();
        $.protocolBalance = 0;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit ProtocolFeesClaimed(feeTo_, amount);
    }

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

**File:** packages/contracts/src/FeeVault.sol (L185-193)
```text
    function setFeeTo(
        address feeTo_
    ) external onlyOwner {
        if (feeTo_ == address(0)) revert ZeroAddress();
        FeeVaultStorage storage $ = _s();
        address old = $.feeTo;
        $.feeTo = feeTo_;
        emit FeeToUpdated(old, feeTo_);
    }
```

**File:** packages/contracts/lib/forge-std/src/StdCheats.sol (L218-220)
```text
        // 4-byte selector for `isBlacklisted(address)`, used by USDC.
        (success, returnData) = token.staticcall(abi.encodeWithSelector(0xfe575a87, addr));
        vm.assume(!success || abi.decode(returnData, (bool)) == false);
```

**File:** docs/contracts-scope.md (L120-121)
```markdown
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
- `transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution.
```
