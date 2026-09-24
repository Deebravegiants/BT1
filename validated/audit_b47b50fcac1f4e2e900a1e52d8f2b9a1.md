### Title
Unguarded division by `ltMinted` in `Zap._executeBuy` panics on legitimate high-`exchangeRate` LT buys - (File: `packages/contracts/src/Zap.sol`)

### Summary
The reported PHP EXIF bug is a classic "unguarded arithmetic operation on attacker/environment-influenced input causes the runtime to abort the transaction" class: a division whose divisor can degenerate to a value the code never checked for. `Zap._executeBuy` contains a structurally identical Solidity analog: `effectiveBaseSpent = (amountInUsed * baseToConvert) / ltMinted` divides by `ltMinted`, the LT amount returned by the external, rebasing-priced BounceTech LT's `mint()` call, without ever checking it for zero.

### Finding Description
In `packages/contracts/src/Zap.sol`, `_executeBuy` computes, on the post-graduation path: [1](#0-0) 
```
baseToConvert = netUsdc;
$.usdc.forceApprove(lt, baseToConvert);
ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0);
tokensOut = _buyOnUniswapV2(tokenAddress, lt, ltMinted);
amountInUsed = ltMinted;
```
and later, unconditionally: [2](#0-1) 
```
uint256 effectiveBaseSpent = (amountInUsed * baseToConvert) / ltMinted;
```
`ltMinted` comes straight from the external LT's `mint()`, defined per `IBounceLeveragedToken.baseToLtAmount` as `baseAmount * 1e18 / exchangeRate()` [3](#0-2) . `exchangeRate()` is an externally driven, unbounded, leverage-amplified price that the docs explicitly describe as live-read and volatile (`docs/contracts-scope.md`, "Exchange-rate freshness on the USD trigger"). As the LT's price appreciates (a normal, expected outcome of a leveraged long/short token over its lifetime), `baseToLtAmount(netUsdc)` for a fixed, minimum-sized `netUsdc` rounds down toward zero. Once `exchangeRate()` exceeds `netUsdc * 1e18`, `mint()` can legitimately return `ltMinted == 0` for a non-zero `baseToConvert`.

On the graduated (post-graduation, HyperSwap) path `amountInUsed` is set equal to `ltMinted`, so both the numerator and denominator of `effectiveBaseSpent = (amountInUsed * baseToConvert) / ltMinted` become `0/0`. Solidity's checked division panics with `Panic(0x12)` (division by zero) — the direct on-chain analog of the reported native SIGFPE: an unguarded division whose divisor was assumed non-zero by the programmer but is actually attacker/market-influenced and can legitimately hit zero.

Any unprivileged trader calling `Zap.buy`/`Zap.buyWithPermit` with `usdcAmount` close to `minUsdcAmount()` on a graduated token whose paired LT has appreciated enough triggers this revert — the transaction reverts entirely (funds are never lost because `usdc.safeTransferFrom` and the panic both roll back atomically), but the call is unconditionally bricked with no recovery path other than sending a larger `usdcAmount`.

### Impact Explanation
This is a denial-of-service on the minimum-size buy path for graduated tokens paired to LTs that have appreciated sufficiently — not a fund-loss bug, since the entire `_buyInternal` call (including the `usdc.safeTransferFrom`) reverts atomically when the `Panic(0x12)` fires; no USDC or tokens ever leave the caller. The severity is bounded: larger buy amounts (`usdcAmount` sized so `baseToLtAmount(netUsdc) > 0`) continue to work normally, so this is not a full/permanent freeze of `Zap.buy` for the token, only of buys near the protocol's own minimum-size floor once the LT's price has grown past that floor's implied LT-per-USDC ratio. It does, however, degrade the UX/reliability guarantee the `minUsdcAmount()` floor is supposed to provide (that a buy of exactly the floor amount always succeeds), and the failure mode is an opaque `Panic(0x12)` rather than a clean, documented revert like the codebase's other guarded floors (`BelowMinAmount`, `BelowMinTransactionSize`).

### Likelihood Explanation
The trigger condition depends purely on market movement of the paired LT's `exchangeRate()`, which is explicitly designed to be unbounded and leverage-amplified per the docs, plus a normal, permissionless call to `Zap.buy` with a minimal `usdcAmount`. No special privilege, front-running, or malicious input crafting is required beyond waiting for/causing the LT price to rise — this is squarely within the class of externally-influenced numeric inputs the rules call out (`exchangeRate` / `baseToLtAmount` reads). Likelihood is Medium: it requires the LT's price to cross a specific (large but not impossible) threshold relative to the fixed `minUsdcAmount()` floor, which is plausible over a leveraged token's operating lifetime but not guaranteed to occur quickly.

### Recommendation
In `Zap._executeBuy`, guard the division at line 386 by checking `ltMinted != 0` before computing `effectiveBaseSpent`, and revert with a clean, documented error (e.g., mirroring `BelowMinAmount`) if `mint()` returns zero LT for a non-zero `baseToConvert`. Equivalently, validate `ltMinted > 0` immediately after the `mint()` call on both the graduated and curve paths, so degenerate zero-mint results are surfaced as an intentional, decodable revert rather than an arithmetic panic.

### Proof of Concept
1. Graduate a token via the normal curve flow (`Bonding.triggerGraduation` / the dual-trigger inline path), so `Zap.buy` routes through the `isGraduated` branch.
2. On the LT paired to that token, drive `exchangeRate()` up (in the mock, `MockLeveragedToken.setExchangeRate`; on a real BounceTech LT, via sustained leveraged price appreciation) past `minUsdcAmount() * 1e18` (6dp USDC vs 18dp rate scale).
3. As any unprivileged trader, call `zap.buy(tokenAddr, zap.minUsdcAmount(), 0, address(0))`.
4. `_executeBuy`'s graduated branch computes `baseToConvert = netUsdc` (a small positive value after the 0.75% fee), calls `mint()`, which returns `ltMinted = 0` because `baseToLtAmount(netUsdc)` rounds to zero at the elevated rate.
5. `amountInUsed = ltMinted = 0`; line 386's `(amountInUsed * baseToConvert) / ltMinted` evaluates `0 / 0`, and the call reverts with `Panic(0x12)` instead of a clean protocol error, even though the trader supplied a valid, floor-compliant `usdcAmount`. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** packages/contracts/src/Zap.sol (L317-322)
```text
        if ($.bonding.isGraduated(tokenAddress)) {
            baseToConvert = netUsdc;
            $.usdc.forceApprove(lt, baseToConvert);
            ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0);
            tokensOut = _buyOnUniswapV2(tokenAddress, lt, ltMinted);
            amountInUsed = ltMinted;
```

**File:** packages/contracts/src/Zap.sol (L386-386)
```text
        uint256 effectiveBaseSpent = (amountInUsed * baseToConvert) / ltMinted;
```

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L31-35)
```text
    /// @notice Equals the LT amount that `mint(_, baseAmount, _)` will produce
    ///         at the current `exchangeRate()`.
    function baseToLtAmount(
        uint256 baseAmount
    ) external view returns (uint256);
```
