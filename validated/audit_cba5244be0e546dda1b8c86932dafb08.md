### Title
Unvalidated `ltAddress` in `Bonding.launch` / `Zap.createToken` lets a creator substitute a malicious "LT" contract as the curve's reserve asset - ([File: packages/contracts/src/Zap.sol])

### Summary
The Dataease bug is a missing "is this URL actually pointed at the component we trust" check: the H2 data source never verifies the JDBC URL prefix, so an attacker swaps in an unrelated (Redshift) driver whose parameters are then trusted and executed as if they came from the expected, safe component. The alt.fun analog is `Zap._createTokenInternal` / `Bonding.launch`, which accept a caller-supplied `params.ltAddress` and, after only a non-zero check, wire it in as the token's entire reserve-asset ("LT") implementation — every subsequent curve, fee, and graduation calculation trusts whatever contract sits at that address to behave like a genuine BounceTech Leveraged Token.

### Finding Description
`Zap._createTokenInternal` validates `params.ltAddress` with nothing more than a zero-address check: [1](#0-0) 

That address is passed straight into `Bonding.launch(params, msg.sender)`, which — per the module's own documentation — pairs every new token with "a BounceTech Leveraged Token (LT) as its reserve asset" and treats `virtualLtReserve`, `exchangeRate()`, `baseToLtAmount()`, `ltToBaseAmount()`, and `minTransactionSize()` on that address as ground truth for curve math and graduation: [2](#0-1) 

Nowhere in the reachable code path (`Zap.createToken`/`createTokenWithPermit` → `Bonding.launch`) is `ltAddress` checked against BounceTech's factory/global-storage registry of legitimate LTs — the only gate found by searching for allowlist/registry patterns (`isAllowed`, `ltRegistry`, `approvedLt`) in `Bonding.sol` returned no such check. This is structurally the same failure as the H2 JDBC issue: the system assumes an address/URL belongs to a specific, safe implementation and never verifies that assumption before treating attacker-supplied parameters read from it (`exchangeRate`, `mint`, `redeem`, `baseToLtAmount`) as authoritative.

Because `Zap._executeBuy` and `Zap._sellInternal` call `IBounceLeveragedToken(lt).mint(...)`, `exchangeRate()`, `baseToLtAmount(...)`, and `redeem(...)` directly on whatever `lt` the creator chose at launch time: [3](#0-2) [4](#0-3) 

a creator who deploys their own contract implementing `IBounceLeveragedToken` (fake `mint`, fake `exchangeRate`, fake `redeem`) fully controls the numbers the whole system treats as the reserve valuation, the graduation threshold arithmetic, and how much real USDC Zap thinks it must pay out on `redeem`.

### Impact Explanation
A malicious "LT" can report an inflated `exchangeRate()`/`baseToLtAmount()` to make the curve believe far more real value has been deposited than actually has, dragging the token toward graduation on fabricated numbers, or it can make `redeem()` return more USDC than the fake LT was ever given, draining Zap's/FeeVault's real USDC held for unrelated, legitimately-launched tokens (since `_sellInternal` calls `redeem(address(this), ...)` on `this` LT and then forwards `usdcOut` from the Zap contract's own balance, not funds sourced solely from that trade). This is concrete theft/insolvency risk against Zap and FeeVault, and can leave the launched token permanently unbacked. It satisfies the "unbacked token or LT payouts" / "FeeVault insolvency" impact bar.

### Likelihood Explanation
Any unprivileged wallet can call `Zap.createToken`/`createTokenWithPermit` with `params.ltAddress` pointed at a contract they deployed themselves — no privileged role, no upgrade, no off-chain component needed. The only real friction is authoring a small `IBounceLeveragedToken`-shaped contract, which is trivial. This makes the path High likelihood, reachable in a single transaction from any address.

### Recommendation
Validate `ltAddress` in `Bonding.launch` (and mirror the check in `Zap._createTokenInternal`) against BounceTech's canonical registry — e.g., `IBounceFactory`/`IBounceGlobalStorage` should expose a way to confirm the address is a genuine, factory-deployed LT — and revert launch if it is not recognized, analogous to requiring the JDBC URL to start with the expected `jdbc:h2` prefix before trusting driver-specific parameters.

### Proof of Concept
1. Attacker deploys `FakeLT` implementing `IBounceLeveragedToken`: `mint()` mints/returns arbitrary "LT" balances without requiring real USDC backing; `exchangeRate()` returns an attacker-chosen value; `redeem()` unconditionally returns a large `grossUsdc` figure regardless of the LT amount burned.
2. Attacker calls `Zap.createToken(params, seedUsdcAmount)` with `params.ltAddress = address(FakeLT)`; passes the `ltAddress == address(0)` check and reaches `Bonding.launch`, which registers `FakeLT` as the token's reserve asset.
3. Attacker (or anyone) calls `Zap.sell`/`Zap.buy` on this token; `_executeBuy`/`_sellInternal` call `mint`/`redeem`/`exchangeRate` on `FakeLT`, which return attacker-chosen figures.
4. `Zap._sellInternal` pays out `usdcOut` from Zap's own USDC balance (shared across all tokens) based on `FakeLT.redeem()`'s fabricated `grossUsdc`, draining USDC that legitimately belongs to traders of other, honestly-launched tokens, and/or artificially pushing the token through `canGraduate`/`triggerGraduation` on fabricated reserve numbers.

### Citations

**File:** packages/contracts/src/Zap.sol (L218-230)
```text
    function _createTokenInternal(
        Bonding.LaunchParams calldata params,
        uint256 seedUsdcAmount
    ) internal returns (address tokenAddr) {
        if (params.ltAddress == address(0)) revert InvalidInput();
        // Mandatory seed buy. See `MIN_SEED_USDC` for the no-cap rationale.
        // Floored at the live mint floor too, so a seed can't pass here and
        // then revert when it's minted (see `minSeedUsdc`).
        if (seedUsdcAmount < minSeedUsdc()) revert BelowMinSeed();

        (tokenAddr,) = _s().bonding.launch(params, msg.sender);
        emit TokenCreated(tokenAddr, msg.sender, params.ltAddress);

```

**File:** packages/contracts/src/Zap.sol (L315-324)
```text
        uint256 baseToConvert;
        uint256 ltMinted;
        if ($.bonding.isGraduated(tokenAddress)) {
            baseToConvert = netUsdc;
            $.usdc.forceApprove(lt, baseToConvert);
            ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0);
            tokensOut = _buyOnUniswapV2(tokenAddress, lt, ltMinted);
            amountInUsed = ltMinted;
        } else {
            uint256 ltIfFull = IBounceLeveragedToken(lt).baseToLtAmount(netUsdc);
```

**File:** packages/contracts/src/Zap.sol (L444-452)
```text
        uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
        if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();

        // Intentional v1 tradeoff: sells only use BounceTech's atomic
        // `redeem()` path (no `prepareRedeem` fallback/queue in Zap). If the
        // LT idle-USDC buffer is temporarily depleted, `redeem` reverts and
        // users must retry in smaller chunks after buffer replenishment.
        // Redeem into this zap (not the user) so we can deduct the fee.
        uint256 grossUsdc = IBounceLeveragedToken(lt).redeem(address(this), ltReceived, 0);
```

**File:** packages/contracts/src/Bonding.sol (L25-61)
```text
/// @title Bonding
/// @notice Constant-product bonding curve for the launchpad. Each token pairs with a
///         BounceTech Leveraged Token (LT) as its reserve asset.
/// @dev Forked from Virtuals Protocol `Bonding.sol`. Key design pillars: virtual
///      reserves on the curve `Pair`, dual-trigger graduation (USD threshold OR
///      curve sellout), two-phase graduation split (phase 1 inline in the
///      threshold-crossing buy, phase 2 permissionless and big-block), dynamic
///      LP seeding (zero-gap between curve close and LP open), and
///      brick-resistance against hostile pre-seeds of the post-grad pair. The
///      most subtle code paths are `_enterGraduating`, `finalizeGraduation`,
///      and `_prepareGraduationLiquidity` — natspec on each function below
///      contains the rationale.
/// @dev Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
///
///      Storage uses ERC-7201 namespaced layout (no `__gap` needed). All
///      mutable state lives in `BondingStorage` at
///      `_BONDING_STORAGE_LOCATION`.
contract Bonding is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    using EnumerableSet for EnumerableSet.AddressSet;

    /// @dev Virtual liquidity seeded at launch, in USDC (18-dp). Every
    ///      `*Usd`-named value and every "USD" figure in this contract is
    ///      a USDC amount scaled to 18-dp: the protocol treats 1 USDC as
    ///      1 USD and holds no price oracle.
    ///      Combined with the LT's launch-time `exchangeRate()` to derive
    ///      the launch-time `virtualLtReserve`, which permanently shapes
    ///      the curve via `K = TOTAL_SUPPLY * virtualLtReserve`. Pairs
    ///      with `Deploy.s.sol::GRADUATION_THRESHOLD_USD` at `$9K`
    ///      (3× peg preserved). Constant — changing it for an existing
    ///      proxy is a no-op because `K` is baked into each `Pair` at
    ///      `mint` and never recomputed.
    uint256 public constant VIRTUAL_LIQUIDITY_USD = 3000 ether;
```
