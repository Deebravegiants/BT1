The `FootiumPrizeDistributor` bug class — a hardcoded/rigid claim recipient that a blacklist-capable ERC20 (USDC) can permanently strand — has a real analog in alt.fun's `FeeVault`.

`FeeVault.claim()` pays out strictly to `msg.sender` from `creatorBalance[msg.sender]`, with no alternate-recipient parameter: [1](#0-0) 

Creator fee balances are accrued under the `creator` address recorded in `Bonding.tokenInfo(token).creator` at the time of each trade: [2](#0-1) 

`Bonding.transferCreator` only redirects *future* attribution — it does not, and cannot, move any USDC balance already sitting in `creatorBalance[oldCreator]` inside `FeeVault`, since `FeeVault` has no awareness of `Bonding`'s creator mapping and exposes no admin/creator-triggered balance-migration path: [3](#0-2) 

Fees are denominated in USDC: [4](#0-3) 

USDC has an on-chain `isBlacklisted` mechanism that reverts transfers to/from flagged addresses — the exact blacklist-token class the external report is about.

### Title
Creator fee balances in FeeVault become permanently unclaimable if the creator address is blacklisted by the USDC fee token - (File: packages/contracts/src/FeeVault.sol)

### Summary
`FeeVault.claim()` transfers a creator's entire pooled USDC balance to `msg.sender` and only `msg.sender`, with no way to specify or redirect to an alternate receiving address. Because the fee asset is USDC — a blacklist-capable ERC20 — an already-accrued `creatorBalance[creator]` becomes permanently frozen the moment that creator's own address is added to USDC's blacklist, mirroring the FootiumPrizeDistributor issue where a fixed recipient baked into the claim path prevents an affected user from ever collecting funds already owed to them.

### Finding Description
`accrue()` credits `creatorBalance[creator]` where `creator` is whatever `Bonding.tokenInfo(token).creator` was at trade time. `claim()` then hardcodes the payout target to `msg.sender`, which must equal the exact address the balance is keyed under: [1](#0-0) 

If that creator address is later blacklisted by USDC, `$.usdc.safeTransfer(msg.sender, amount)` will revert for as long as the blacklist entry stands (USDC blacklisting is generally permanent absent Circle intervention). `Bonding.transferCreator(tokenAddress, newCreator)` exists to rotate the creator role, but it only mutates `TokenInfo.creator` for *future* `_accrueFee` calls — it has no effect on, and no interface into, the USDC balance already sitting in `FeeVault.creatorBalance[oldCreator]`: [3](#0-2) 

There is no owner-level or creator-level recovery function in `FeeVault` to sweep or reassign a specific creator's stranded balance to a new address — only `sweepDonations()` exists, and it only ever sweeps *unbacked* surplus USDC (balance above `totalAccruedCreator + protocolBalance`), which explicitly excludes any already-backed `creatorBalance` entry: [5](#0-4) 

### Impact Explanation
Any creator whose launch address becomes USDC-blacklisted (a real-world scenario handled explicitly elsewhere in this codebase's own dependency tree, e.g. `assumeNotBlacklisted` cheats for USDC/USDT in `forge-std`) permanently loses access to all currently accrued and any future-until-rotation 0.25% creator fee share tied to that address. Because `FeeVault` sizes its balances against `totalAccruedCreator` for its underfund check, the funds remain locked inside the vault indefinitely — they are neither claimable by the blacklisted creator nor recoverable by anyone else, constituting a permanent freeze of creator funds.

### Likelihood Explanation
Reaching this state requires no privileged action by alt.fun — it only requires USDC's centralized blacklist authority (Circle) to blacklist the specific address a token creator used at launch, which is an externally-triggered but realistic and previously-exploited condition for USDC holders. Once blacklisted, every subsequent unprivileged `claim()` call from that address deterministically reverts, and no other on-chain path in `FeeVault` or `Bonding` moves the already-accrued balance to a fresh address.

### Recommendation
Add a `claimTo(address to)` variant (or parameterize `claim`) that lets `msg.sender` designate an arbitrary, non-zero recipient for their own `creatorBalance`, verified against `msg.sender` rather than baking the recipient into any fixed value. Additionally, extend `Bonding.transferCreator` (or add a dedicated `FeeVault` admin/owner function) to migrate an already-accrued `creatorBalance[oldCreator]` to `newCreator` when the creator role is transferred, so a blacklisted creator can escape via `transferCreator` plus a balance migration rather than being permanently locked out.

### Proof of Concept
1. Creator `C` launches a token via `Zap.createToken`, accrues creator fees over several buys/sells; `FeeVault.creatorBalance(C)` grows to `X` USDC.
2. USDC blacklists address `C` (external, centralized action — outside alt.fun's control but a documented USDC feature).
3. `C` calls `Bonding.transferCreator(token, newAddr)` to redirect future fees — this only updates `TokenInfo.creator`; `FeeVault.creatorBalance(C)` remains `X`.
4. `C` (or anyone acting on `C`'s behalf) calls `FeeVault.claim()` — `$.usdc.safeTransfer(C, X)` reverts because `C` is blacklisted by USDC.
5. `X` USDC remains permanently locked inside `FeeVault`: it counts toward `totalAccruedCreator`, so `sweepDonations()` cannot touch it, and no other function can redirect or release it.

### Citations

**File:** packages/contracts/src/FeeVault.sol (L127-135)
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
```

**File:** packages/contracts/src/FeeVault.sol (L151-160)
```text
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

**File:** packages/contracts/src/Zap.sol (L476-487)
```text
    function _accrueFee(
        address token,
        address creator,
        uint256 feeAmount,
        bool isBuy
    ) internal {
        ZapStorage storage $ = _s();
        uint256 creatorShare = (feeAmount * $.creatorFeeBps) / BPS_DENOM;
        uint256 protocolShare = feeAmount - creatorShare;
        $.usdc.safeTransfer(address($.feeVault), feeAmount);
        $.feeVault.accrue(token, creator, creatorShare, protocolShare, isBuy);
    }
```

**File:** packages/contracts/src/Bonding.sol (L738-748)
```text
    function transferCreator(
        address tokenAddress,
        address newCreator
    ) external {
        if (newCreator == address(0)) revert ZeroAddress();
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (msg.sender != info.creator) revert NotCreator();
        if (newCreator == info.creator) revert InvalidInput();
        info.creator = newCreator;
        emit CreatorTransferred(tokenAddress, msg.sender, newCreator);
    }
```

**File:** docs/contracts-scope.md (L114-121)
```markdown
All fees are charged by `Zap` in USDC and forwarded into `FeeVault`. The router holds no fee state — the vault is where balances live and where creators and the protocol claim.

- **Rate:** 0.75% on every buy/sell (curve **and** post-grad), split 0.5% protocol / 0.25% creator.
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
- **Lifetime counters:** `lifetimeCreatorEarned(creator)` / `lifetimeProtocolEarned` never decrement on claim, so the UI can render "total earned / claimed / claimable" consistently.
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
- `transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution.
```
