### Title
`Bonding.initializeBounceGlobalStorage` has no access control and can be front-run to hijack `bounceGlobalStorage` - (File: packages/contracts/src/Bonding.sol)

### Summary
`Bonding.initializeBounceGlobalStorage` is guarded only by `reinitializer(2)` with no `onlyOwner` (or any caller check), mirroring the Teller `CollateralManager.setCollateralEscrowBeacon` finding: any address can call it, and its only safety check is that `bounceGlobalStorage` must still be `address(0)`. [1](#0-0) 

### Finding Description
`initializeBounceGlobalStorage` is meant to backfill the `bounceGlobalStorage` pointer on a proxy that predates that slot, and the natspec explicitly says the `address(0)` guard is intended to "close the reinitializer-front-run window on fresh proxies that haven't been initialised yet" — but the function itself carries no `onlyOwner`/`onlyOwner`-style restriction, only `reinitializer(2)`: [1](#0-0) 

Because it is `external` with no caller check, any unrelated wallet watching the mempool for the operator's `upgradeToAndCall` (or a plain call to this reinitializer on a freshly-deployed but not-yet-backfilled proxy) can front-run it with their own transaction supplying an attacker-controlled `bounceGlobalStorage_` address. Since the guard only checks `address($.bounceGlobalStorage) != address(0)`, the attacker's call succeeds first and permanently locks in the malicious pointer (the version-2 reinitializer slot is consumed and can never be replayed). [2](#0-1) 

`bounceGlobalStorage` is not a passive pointer — it is used in the permissionless `launch()` path to resolve the live BounceTech `Factory` and validate that a launch's `ltAddress` is a legitimate BounceTech LT: [3](#0-2) 
and its role is described directly in storage docs as the trust anchor rejecting non-BounceTech LTs, "which could otherwise siphon buyer USDC inside `mint`": [4](#0-3) 

If the attacker's malicious `bounceGlobalStorage` points to a fake `IBounceGlobalStorage`/`IBounceFactory` whose `ltExists()` always returns `true`, `launch()`'s only defense against arbitrary "LT" contracts is defeated — any creator (or the attacker itself) could then launch a token backed by a fully malicious "LT" contract. Since `Zap`'s buy path `forceApprove`s USDC into the LT for `mint()` and trusts LT-reported `exchangeRate()`/balances, a malicious LT admitted this way can siphon buyer USDC directly inside `mint`, exactly the risk the storage doc warns about.

### Impact Explanation
This is a High-severity issue: an unprivileged attacker permanently overwrites a security-critical validation pointer that the entire launch flow depends on to keep out malicious reserve-asset contracts. Once hijacked, the attacker (or anyone) can launch tokens paired to attacker-controlled fake LTs; each `Zap.createToken`/`buy` against those tokens routes real USDC into the malicious LT's `mint()`, resulting in concrete theft of trader funds. Because `reinitializer(2)` can only fire once, the corruption is irreversible without a further UUPS upgrade (a privileged, out-of-band remediation).

### Likelihood Explanation
Likelihood is High whenever this reinitializer has not yet been called on a live proxy: it requires only a plain mempool-observed transaction (no special access, no flash loan, no timing beyond “front-run this one specific, low-frequency admin call”), and the function's own natspec acknowledges the front-run window exists — it just wrongly assumes the `address(0)` check is a sufficient defense rather than access control.

### Recommendation
Add `onlyOwner` to `initializeBounceGlobalStorage`, matching the pattern already used on `setBounceGlobalStorage`:
```solidity
function initializeBounceGlobalStorage(
    address bounceGlobalStorage_
) external reinitializer(2) onlyOwner {
    ...
}
```
This preserves the intended one-time backfill semantics of `reinitializer(2)` while removing the front-runnable single point of failure.

### Proof of Concept
1. Deploy/observe a `Bonding` proxy that has not yet called `initializeBounceGlobalStorage` (post-upgrade, pre-backfill state, `bounceGlobalStorage == address(0)`). [5](#0-4) 
2. Attacker deploys a malicious `FakeGlobalStorage` contract whose `factory()` returns a `FakeFactory` whose `ltExists(address)` always returns `true`.
3. Attacker calls `bonding.initializeBounceGlobalStorage(address(fakeGlobalStorage))` before the legitimate owner's call lands (front-run via higher gas / same-block ordering).
4. `$.bounceGlobalStorage` is now permanently set to the attacker's contract; the legitimate call reverts with `InvalidInput()` because the zero-address guard now fails. [6](#0-5) 
5. Attacker calls `Zap.createToken(...)` with `ltAddress` pointing to a malicious LT contract; `launch()`'s `ltExists` check passes against the fake factory: [3](#0-2) 
6. Subsequent buyers' USDC is minted into the attacker's malicious LT via `Zap`'s `forceApprove`/`mint` flow and can be drained by the attacker, realizing direct theft of trader funds.

### Citations

**File:** packages/contracts/src/Bonding.sol (L220-225)
```text
        /// @dev BounceTech `GlobalStorage`, queried per-launch to resolve the
        ///      live `Factory` and reject non-BounceTech LTs (which could
        ///      otherwise siphon buyer USDC inside `mint`). Going through
        ///      `GlobalStorage` means BounceTech `setFactory` rotations flow
        ///      through automatically.
        IBounceGlobalStorage bounceGlobalStorage;
```

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

**File:** packages/contracts/src/Bonding.sol (L396-401)
```text
        // `Zap.createToken` is permissionless; without this gate a fake LT
        // could siphon USDC inside `mint` (which `Zap` `forceApprove`s).
        if (!IBounceFactory($.bounceGlobalStorage.factory()).ltExists(params.ltAddress)) {
            revert UnknownLeveragedToken(params.ltAddress);
        }

```
