### Title
Missing access-control on `Bonding.initializeBounceGlobalStorage` allows front-running to inject a malicious `bounceGlobalStorage`, bypassing the BounceTech LT-existence gate - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.initializeBounceGlobalStorage` is a `reinitializer(2)` backfill function that sets the critical `bounceGlobalStorage` reference used to validate leveraged tokens (LTs) on every launch, but unlike every other privileged setter in the contract it carries no `onlyOwner` modifier.

### Finding Description
`initializeBounceGlobalStorage` is guarded only by `reinitializer(2)` and a "set-once" check (`if (address($.bounceGlobalStorage) != address(0)) revert InvalidInput();`) — there is no `onlyOwner` (or any caller restriction) on the function itself, unlike the analogous audit finding in Teller's `CollateralManager.setCollateralEscrowBeacon()`: [1](#0-0) 

The natspec even acknowledges a front-run window exists ("The `address(0)` guard closes the reinitializer-front-run window on fresh proxies that haven't been initialised yet"), but the guard only makes the write idempotent — it does not stop an unprivileged address from being the *first* to set the value. If the owner performs the UUPS upgrade to the new implementation and calls `initializeBounceGlobalStorage` in a **separate** transaction from the upgrade itself (rather than atomically via `upgradeToAndCall(newImpl, data)`), any address can race that owner transaction and call `initializeBounceGlobalStorage(maliciousAddr)` first, since the function has no `onlyOwner` gate, permanently locking in the attacker-controlled address (the `address(0)` guard then blocks the legitimate owner call from ever correcting it).

`bounceGlobalStorage` is not a decorative reference — it is the sole source of truth for the anti-fake-LT gate in `Bonding.launch()`: [2](#0-1) 

and is also read directly by `Zap.minUsdcAmount()` (`_s().bonding.bounceGlobalStorage().minTransactionSize()`), which every buy/sell path in `Zap` uses as its minimum-transaction floor: [3](#0-2) 

If an attacker plants a malicious `IBounceGlobalStorage` implementation, they control (a) the `factory()` address returned to `Bonding.launch`'s `ltExists` check, and (b) the `minTransactionSize()` floor read by `Zap`. Test coverage in `BounceFactoryGate.t.sol` explicitly documents that this gate exists precisely to reject "a brand-new LT that exists on-chain but was never registered with BounceTech": [4](#0-3) 

A malicious `bounceGlobalStorage.factory()` can return a fake `IBounceFactory` whose `ltExists()` always returns `true`, letting the attacker launch tokens paired with an arbitrary, attacker-authored "LT" contract. `Zap._executeBuy` then `forceApprove`s that contract for the buyer's USDC and calls `mint()`/`redeem()` on it: [5](#0-4) 

A malicious LT contract can simply pull the approved USDC without returning any real LT, or return the same amount it took but never fund `redeem`, stealing buyer USDC.

### Impact Explanation
Successful exploitation lets an attacker permanently seize the LT-registry integrity check that `Bonding.launch` relies on, opening the door to launching tokens backed by malicious LT contracts that drain buyer USDC via `Zap`'s `mint`/`redeem` calls — direct theft of trader funds. This matches the "concrete theft of trader funds" acceptance bar. Because the write is idempotent (`address(0)` check), the corruption is permanent and unrecoverable without a further UUPS upgrade.

### Likelihood Explanation
The bug requires a specific but plausible operational sequence: the owner upgrades `Bonding` to a version containing `initializeBounceGlobalStorage` without atomically calling it in the same `upgradeToAndCall` transaction. Once the new implementation is live and before the owner's follow-up call lands, any address can front-run it in the same or an earlier block since the function is public and unguarded. This is a realistic deployment/upgrade-timing risk rather than a hypothetical one, and the code's own comments show the team was aware of (but did not fully close) this race.

### Recommendation
Add `onlyOwner` to `initializeBounceGlobalStorage`, mirroring the fix recommended in the source report for `setCollateralEscrowBeacon` (add `onlyTellerV2`/equivalent privileged-caller modifier), so that only the contract owner can ever supply the `bounceGlobalStorage` reference, removing the front-run window entirely regardless of whether the initialization call is bundled atomically with the upgrade.

### Proof of Concept
1. Owner deploys and upgrades `Bonding` proxy via `UUPSUpgradeable.upgradeToAndCall(newImpl, "")` (no atomic init data) — the new implementation exposes `initializeBounceGlobalStorage`.
2. Attacker, monitoring the mempool/chain state, immediately calls `bonding.initializeBounceGlobalStorage(maliciousStorage)` where `maliciousStorage.factory()` returns an attacker-controlled `IBounceFactory` whose `ltExists(any)` always returns `true`.
3. Because `Bonding.bounceGlobalStorage` was still `address(0)`, the call succeeds and permanently locks in the attacker's address (owner's later legitimate call reverts with `InvalidInput`).
4. Attacker calls `Zap.createToken` / `createTokenWithPermit` with `params.ltAddress` pointing at a self-authored fake LT contract; `Bonding.launch`'s gate check at [6](#0-5)  passes because the malicious factory reports the fake LT as existing.
5. Victims call `Zap.buy`, which `forceApprove`s USDC to the fake LT and calls `mint()` [7](#0-6) ; the fake LT contract pulls the approved USDC and either mints nothing back or refuses `redeem`, resulting in stolen buyer funds.

### Citations

**File:** packages/contracts/src/Bonding.sol (L374-386)
```text
    /// @notice Backfill `bounceGlobalStorage` on a proxy deployed before this
    ///         slot existed. Invoked atomically via `upgradeToAndCall`. The
    ///         `address(0)` guard closes the reinitializer-front-run window on
    ///         fresh proxies that haven't been initialised yet.
    function initializeBounceGlobalStorage(
        address bounceGlobalStorage_
    ) external reinitializer(2) {
        if (bounceGlobalStorage_ == address(0)) revert ZeroAddress();
        BondingStorage storage $ = _s();
        if (address($.bounceGlobalStorage) != address(0)) revert InvalidInput();
        $.bounceGlobalStorage = IBounceGlobalStorage(bounceGlobalStorage_);
        emit BounceGlobalStorageUpdated(address(0), bounceGlobalStorage_);
    }
```

**File:** packages/contracts/src/Bonding.sol (L394-400)
```text
        if (params.ltAddress == address(0)) revert InvalidInput();
        BondingStorage storage $ = _s();
        // `Zap.createToken` is permissionless; without this gate a fake LT
        // could siphon USDC inside `mint` (which `Zap` `forceApprove`s).
        if (!IBounceFactory($.bounceGlobalStorage.factory()).ltExists(params.ltAddress)) {
            revert UnknownLeveragedToken(params.ltAddress);
        }
```

**File:** packages/contracts/src/Zap.sol (L315-320)
```text
        uint256 baseToConvert;
        uint256 ltMinted;
        if ($.bonding.isGraduated(tokenAddress)) {
            baseToConvert = netUsdc;
            $.usdc.forceApprove(lt, baseToConvert);
            ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0);
```

**File:** packages/contracts/src/Zap.sol (L628-635)
```text
    /// @notice Live BounceTech `mint`/`redeem` floor in USDC (6dp), sourced
    ///         from `GlobalStorage` so a change to their floor is honoured
    ///         without a redeploy. Used as the pre-flight buy/sell minimum
    ///         and as the graduation floor-bump target; also surfaced for
    ///         off-chain callers sizing minimum trades.
    function minUsdcAmount() public view returns (uint256) {
        return _s().bonding.bounceGlobalStorage().minTransactionSize();
    }
```

**File:** packages/contracts/test/BounceFactoryGate.t.sol (L56-66)
```text
    function test_launch_revertsOnUnregisteredLT() public {
        // Brand-new LT that exists on-chain but was never registered with
        // BounceTech — exactly the malicious-LT case described in the issue.
        MockLeveragedToken rogueLT =
            new MockLeveragedToken("Rogue", "ROGUE", LT_EXCHANGE_RATE, 2, true, "ROGUE", address(usdc));

        Bonding.LaunchParams memory params = _launchParams(address(rogueLT));
        vm.prank(creator);
        vm.expectRevert(abi.encodeWithSelector(Bonding.UnknownLeveragedToken.selector, address(rogueLT)));
        bonding.launch(params, creator);
    }
```
