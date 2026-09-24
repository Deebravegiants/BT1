### Title
Creator fee balances can be permanently trapped in `FeeVault` if the creator's address is later blocklisted by USDC - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.claim()` hardcodes the payout recipient to `msg.sender` with no mechanism to redirect an individual creator's accrued balance to a different address. If a creator's own wallet is ever placed on the USDC blocklist (or otherwise made unable to receive USDC transfers), their `creatorBalance[msg.sender]` becomes permanently unclaimable — the same "blocked recipient traps funds" bug class described in the external report, but here the trapped funds sit in `FeeVault` instead of `QVSimpleStrategy`.

### Finding Description
`FeeVault.accrue()` credits a creator's fee share to `creatorBalance[creator]`, where `creator` comes from `Bonding.tokenInfo(token).creator` at the time each buy/sell fee is settled via `Zap._accrueFee`. [1](#0-0) 

The only way to withdraw that balance is `claim()`, which unconditionally sends the USDC to `msg.sender`: [2](#0-1) 

There is no function anywhere in `FeeVault` that lets a creator specify an alternate payout address, and no owner/admin override that can redirect or rescue an individual creator's `creatorBalance` entry — the only owner-controlled redirect is `setFeeTo`, which only affects the pooled `protocolBalance`, not per-creator balances: [3](#0-2) 

`Bonding.transferCreator` changes only the token's `creator` field going forward — it governs future fee *attribution*, not the already-accrued `creatorBalance[oldCreator]` sum sitting in the vault, which remains keyed to the old (now possibly blocklisted) address: [4](#0-3) 

Since fees are USDC (an admin-blocklistable token per `docs/contracts-scope.md`'s fee description) and `claim()`'s `safeTransfer(msg.sender, amount)` will revert for as long as `msg.sender` is blocklisted, any USDC already accrued to that creator becomes permanently stuck with no recovery path — mirroring the report's root cause: a hardcoded recipient address that can't be updated and no fallback withdraw function for the pool operator. [5](#0-4) 

### Impact Explanation
Any USDC already credited to `creatorBalance[creator]` before the creator's address is blocklisted is permanently frozen in `FeeVault` — it can never be claimed by that creator (their own transfer target is blocklisted) nor by anyone else (no admin rescue path exists for per-creator balances). This is a real, permanent loss of creator funds, distinct from the fixable `claimProtocol`/`setFeeTo` path.

### Likelihood Explanation
This requires only that a creator's own wallet becomes subject to a USDC-level restriction (blocklisting, sanctions, or a compliance freeze) at some point after fees have accrued — a scenario acknowledged as realistic in the very report this analog is based on for USDC/USDT. No privileged protocol action or attacker collusion is needed to trigger the freeze; it's purely a function of USDC's own admin blocklist interacting with the vault's hardcoded-recipient `claim()` design.

### Recommendation
Add a mechanism analogous to `setFeeTo` but scoped to individual creators — e.g., a `claimTo(address to)` function (self-authorized by `msg.sender == creator`) that lets a creator redirect their own payout to an alternate address, or an owner-gated emergency `rescueCreatorBalance(address creator, address to)` function for cases where the creator's own address is unusable.

### Proof of Concept
1. `depositor` (an allowlisted `Zap`) calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)` multiple times as trades occur, building up `creatorBalance[creator]` in USDC — as shown in `test_accrue_tracksTotalAccruedCreator` and `test_claim_paysOutAndResetsBalance`. [6](#0-5) 
2. USDC's centralized admin adds `creator`'s address to its blocklist (a real, documented USDC capability referenced in the source report).
3. `creator` calls `FeeVault.claim()`. `$.usdc.safeTransfer(msg.sender, amount)` reverts because `msg.sender` (the creator) is blocklisted by USDC. [2](#0-1) 
4. `creator` calls `Bonding.transferCreator(tokenAddress, newAddress)` to change future attribution, but this does not move the already-accrued `creatorBalance[creator]` sitting in `FeeVault` — that balance is still indexed by the old, blocklisted address. [4](#0-3) 
5. No other function in `FeeVault` (`claimProtocol`, `sweepDonations`, `setFeeTo`, `addDepositor`, `removeDepositor`) can move or reroute `creatorBalance[creator]` — the funds are permanently stuck in the contract.

### Citations

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

**File:** packages/contracts/src/FeeVault.sol (L179-193)
```text
    /// @notice Set the protocol fee recipient.
    /// @dev Protocol fees are pooled and paid to whoever is `feeTo` at claim
    ///      time, so rotating here redirects the entire outstanding
    ///      `protocolBalance` — and any sweepable donations — to `feeTo_`. Call
    ///      `claimProtocol()` (and `sweepDonations()`) first to settle the
    ///      pending balance to the current recipient before rotating.
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

**File:** docs/contracts-scope.md (L114-118)
```markdown
All fees are charged by `Zap` in USDC and forwarded into `FeeVault`. The router holds no fee state — the vault is where balances live and where creators and the protocol claim.

- **Rate:** 0.75% on every buy/sell (curve **and** post-grad), split 0.5% protocol / 0.25% creator.
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
```

**File:** packages/contracts/test/FeeVault.t.sol (L239-257)
```text
    function test_claim_paysOutAndResetsBalance() public {
        vault.addDepositor(depositor);
        usdc.mint(address(vault), 100 ether);
        vm.prank(depositor);
        vault.accrue(address(0xbeef), creator, 20 ether, 80 ether, true);

        vm.expectEmit(true, false, false, true);
        emit FeeVault.CreatorFeesClaimed(creator, 20 ether);
        vm.prank(creator);
        uint256 claimed = vault.claim();

        assertEq(claimed, 20 ether);
        assertEq(usdc.balanceOf(creator), 20 ether);
        assertEq(vault.creatorBalance(creator), 0);
        // Lifetime is never reset.
        assertEq(vault.lifetimeCreatorEarned(creator), 20 ether);
        // Running counter decremented so it stays in sync with the claim mapping.
        assertEq(vault.totalAccruedCreator(), 0);
    }
```
