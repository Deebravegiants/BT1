No vulnerability found for this question.

The reported bug class is a royalty-array truncation issue: an unbounded `creatorRecipients` array is silently capped at `MAX_ROYALTY_RECIPIENTS_INDEX`, causing later (often larger) royalty shares to be dropped and unpaid. Checking alt.fun's actual fee-splitting logic, there is no analogous multi-recipient array or truncation risk:

- `Zap._accrueFee` computes a simple two-way split (`creatorShare` / `protocolShare`) via fixed-point math and always credits both parties in full — no iteration over a variable-length recipient list, no cap, no truncation. [1](#0-0) 
- `FeeVault.accrue` only tracks a single `creatorBalance[creator]` and a single `protocolBalance`, with an O(1) underfund check — there's no concept of a recipient array of unbounded/variable size that could be truncated. [2](#0-1) 
- Per the docs, referral tracking exists only for off-chain indexing with explicitly "No on-chain fee split in v1," and creator attribution is a single address (`Bonding.tokenInfo(token).creator`, updatable via `transferCreator`), not a list of recipients. [3](#0-2) 

Since alt.fun's fee/royalty-equivalent logic has no arbitrary-length recipient array or index cap anywhere in the reachable unprivileged paths (`Zap.buy`/`sell`, `FeeVault.claim`/`claimProtocol`), the root cause of the reported bug class (silent truncation of an oversized recipient array) does not exist in this codebase.

### Citations

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

**File:** docs/contracts-scope.md (L112-129)
```markdown
## Fees & FeeVault

All fees are charged by `Zap` in USDC and forwarded into `FeeVault`. The router holds no fee state — the vault is where balances live and where creators and the protocol claim.

- **Rate:** 0.75% on every buy/sell (curve **and** post-grad), split 0.5% protocol / 0.25% creator.
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
- **Lifetime counters:** `lifetimeCreatorEarned(creator)` / `lifetimeProtocolEarned` never decrement on claim, so the UI can render "total earned / claimed / claimable" consistently.
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
- `transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution.

---

## Referral Tracking

- `buy()` accepts optional `referrer` address
- Emits `Referred(token, trader, referrer, usdcAmount)` for off-chain indexing
- No on-chain fee split in v1
```
