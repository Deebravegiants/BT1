### Title
Creator fee claims permanently DoS'd for a USDC-blacklisted creator - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.claim()` pays a creator's entire pooled USDC balance in a single `safeTransfer` to `msg.sender`, with no fallback, pull-based escrow, or admin-redirect path if that transfer reverts.

### Finding Description
`claim()` zeroes `creatorBalance[msg.sender]` and `totalAccruedCreator` *before* calling `$.usdc.safeTransfer(msg.sender, amount)`: [1](#0-0) 

The vault holds real USDC (`$.usdc` set at `initialize`) as the reserve/fee asset used across the protocol: [2](#0-1) 

Production USDC (Circle's token) enforces an issuer-controlled blacklist that makes `transfer`/`transferFrom` revert for a blacklisted address on either the sender or receiver side. If a creator's address is ever placed on that blacklist — for any reason unrelated to alt.fun (e.g. flagged by Circle's compliance process, sanctioned counterparty interaction, etc.) — every call to `claim()` from that address reverts unconditionally at the `safeTransfer` step, because `IERC20.transfer` to a blacklisted recipient always reverts on real USDC. There is no try/catch, no alternate withdrawal address, and no owner-side rescue path for an individual creator's `creatorBalance` (the only privileged levers, `setFeeTo`/`addDepositor`/`removeDepositor`, cannot redirect a specific creator's balance). Because `creatorBalance[msg.sender]` is only ever written by `accrue` (increasing it) and `claim` (zeroing it on success), a permanently-reverting `claim` leaves that creator's accrued USDC pooled in the vault forever, with a fee split of 0.25% of every buy/sell on their launched tokens — see `Zap`'s fee flow that feeds `accrue`: [3](#0-2) 

This is the direct structural analog of the reported `SdtRewardReceiver::_withdrawRewards` issue: a single non-catchable token-transfer failure to a legitimately blacklisted recipient blocks that recipient's entire claim path, with no workaround, because the payout function makes one all-or-nothing external transfer instead of a pull-based or per-token isolated design.

### Impact Explanation
Any creator whose wallet becomes USDC-blacklisted permanently loses access to their entire outstanding creator fee balance — funds that continue to accrue from every buy/sell of the tokens they launched (`accrue` keeps incrementing `creatorBalance`/`totalAccruedCreator` for their address on every trade). This is a permanent freeze of legitimate creator funds with no recovery mechanism, matching the "permanent freezing of ... creator ... funds" acceptance criterion.

### Likelihood Explanation
Medium: it requires the creator's address to become USDC-blacklisted, an event outside the protocol's control but a real, non-hypothetical risk given Circle's active compliance blacklisting of USDC addresses. No privileged action, upgrade, or malicious actor within alt.fun is needed — any unrelated USDC compliance action against the creator's own address triggers the DoS the next time they call the permissionless `claim()`.

### Recommendation
Make `claim()` resilient to a reverting transfer: e.g. wrap the `safeTransfer` in a try/catch and, on failure, keep the creator's balance un-zeroed (or move it to a separate "stuck" escrow claimable via `IERC20.transfer` from a different address the creator controls), or support a creator-specified alternate recipient for the payout so a blacklisted address is not the sole possible destination.

### Proof of Concept
1. A creator launches a token via `Bonding`/`Zap` and accrues creator fees over time through `FeeVault.accrue`, growing `creatorBalance[creator]`.
2. The creator's wallet is later added to USDC's blacklist by Circle (independent of alt.fun).
3. The creator calls `FeeVault.claim()`; the internal `$.usdc.safeTransfer(msg.sender, amount)` reverts because USDC's `transfer` to a blacklisted address always reverts.
4. Every subsequent call to `claim()` from that address reverts identically. `creatorBalance[creator]` is never zeroed and there is no other function that lets the creator (or the protocol owner) redirect or recover that specific balance — the funds are permanently stuck in `FeeVault`.

### Citations

**File:** packages/contracts/src/FeeVault.sol (L83-92)
```text
    function initialize(
        address usdc_,
        address feeTo_
    ) external initializer {
        if (usdc_ == address(0) || feeTo_ == address(0)) revert ZeroAddress();
        __Ownable_init(msg.sender);
        FeeVaultStorage storage $ = _s();
        $.usdc = IERC20(usdc_);
        $.feeTo = feeTo_;
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
