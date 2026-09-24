Based on the codebase evidence, the strongest reachable analog for the CVE's "repeatable crash/hang via a legitimate operation" bug class in alt.fun is a donation-triggered panic revert in `Router._computeBuy`'s overflow-cap logic.

### Title
Donating launched-Token supply directly to the `Pair` corrupts the virtual-reserve gap and turns the overflow-buy-cap safety net into a repeatable revert (`Router._computeBuy`)

### Summary
`Router._computeBuy` relies on an invariant — "the pair's real token balance is always strictly less than the stored (virtual) `tokenReserve`" — to gracefully cap oversized buys instead of over-paying. [1](#0-0)  This invariant is not actually enforced on-chain; it only holds as long as nobody sends `Token` directly to the `Pair` outside the normal buy/sell flow. Since the launched `Token` is a completely standard, freely-transferable ERC20 [2](#0-1) , any unrelated wallet can transfer tokens straight into a live `Pair`, inflating `tokenBalance()` relative to the stored `tokenReserve` and shrinking or eliminating the gap that the overflow cap depends on.

### Finding Description
On every normal buy, `Pair.swap` decrements the stored `tokenReserve` by exactly `tokensOut`, and `Pair.transferToken` moves the same `tokensOut` out of the pair's real balance — so the gap between `tokenReserve` and `tokenBalance()` stays fixed at the launch-time virtual reserve (`LP_RESERVE = 250M`), as asserted by `test_inv_virtualReserveAlwaysExceedsRealBalance`. [3](#0-2) 

That gap is only ever *reduced by real sells and buys*; nothing stops an outside address from closing it artificially by acquiring launched tokens on the curve and then donating them back to the `Pair` with a plain `IERC20.transfer`. Once `tokenBalance() >= tokenReserve`, any buy whose uncapped `tokensOut` exceeds the (now inflated) real balance enters the capping branch:

```solidity
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;
    uint256 cappedReserveToken = reserveToken - tokensOut;   // underflows or == 0
    if (cappedReserveToken == 0) revert OverflowCapDegenerate();
    ...
}
``` [1](#0-0) 

If `realBalance == reserveToken`, this hits the explicit `OverflowCapDegenerate` revert; if `realBalance > reserveToken`, the subtraction underflows and reverts with a raw Solidity panic — both are unconditional reverts. This is exactly the code path the project's own comments describe as "unreachable... if it ever ceased to hold, that branch would revert... rather than over-pay," i.e., the developers assumed the invariant is always intact and used the revert only as a last-resort defensive backstop, not as an attacker-reachable trigger. [4](#0-3) 

`Zap.buy`'s whole reason for calling into this cap logic is to gracefully handle any buy that requests more than the curve has left, refunding the LT/USDC excess in the same transaction. [5](#0-4)  Because ordinary users size buys in round USDC amounts (not curve-precise LT amounts), oversized buys near the tail of a curve are a normal occurrence, not an edge case — this is exactly the scenario `Router.buy`'s cap and `test_inv_overflowCap_refundsLt` exist to cover. [6](#0-5) 

### Impact Explanation
Once the gap is corrupted, any legitimate oversized buy that would normally be gracefully capped and refunded instead reverts outright — a repeatable "crash" of the core buy path for that token, mirroring the CVE's "easily exploitable... repeatable crash" characterization. For a token whose price never pumps enough to satisfy the USD graduation trigger (the documented "flat/bear market" case the supply trigger exists for) [7](#0-6) , reaching `tokenBalance() == 0` to graduate now requires every remaining buyer to submit a curve-perfectly-sized transaction instead of relying on the built-in overflow protection; any ordinary rounded buy attempt reverts instead of completing. This degrades the protocol's graduation guarantee and denial-of-service's normal trading/graduation flow for affected tokens, at the cost of an attacker who must acquire and donate roughly the 250M-token virtual gap.

### Likelihood Explanation
Medium. The attack requires no privileges — any wallet can buy tokens on the curve and transfer (`IERC20.transfer`) them straight into the public `Pair` address — but it does require enough capital to acquire close to the 250M-token virtual gap before donating, which is a real but bounded cost tied to the curve's `$9K` graduation raise size.

### Recommendation
`Router._computeBuy` should derive the "real" sellable balance from the router/pair's own accounted state (e.g., tracking cumulative tokens transferred out rather than trusting a live `balanceOf`), or explicitly clamp `tokensOut` to `min(realBalance, reserveToken - 1)` and handle the degenerate/underflow case by falling back to a zero-output no-op rather than reverting the whole buy, so a corrupted gap degrades gracefully instead of bricking oversized buys.

### Proof of Concept
1. Launch a token; `Pair.tokenReserve = 1e9`, `tokenBalance() = 750e6` (gap = `LP_RESERVE = 250e6`).
2. Attacker buys ~250e6 tokens on the curve via `Zap.buy`/`Bonding.buy` (paying the curve price).
3. Attacker calls `Token.transfer(pair, ~250e6 tokens)` directly, bypassing `Router`/`Bonding` entirely — a plain ERC20 transfer, not gated by any role.
4. Now `pair.tokenBalance() ≈ pair.getReserves().tokenReserve` (gap ≈ 0).
5. Any subsequent buyer who submits an oversized LT amount (as `test_inv_overflowCap_refundsLt` does with `1_000_000_000 ether`) now hits `Router._computeBuy`'s cap branch and reverts with `OverflowCapDegenerate` or a raw arithmetic-underflow panic instead of completing with a capped fill + refund. [6](#0-5)

### Citations

**File:** packages/contracts/src/Router.sol (L140-147)
```text
        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
```

**File:** packages/contracts/src/Token.sol (L18-35)
```text
contract Token is Initializable, ERC20Upgradeable, ERC20PermitUpgradeable, OwnableUpgradeable {
    uint256 public constant TOTAL_SUPPLY = 1_000_000_000 ether;

    constructor() {
        _disableInitializers();
    }

    function initialize(
        string memory name_,
        string memory symbol_,
        address owner_
    ) external initializer {
        __ERC20_init(name_, symbol_);
        __ERC20Permit_init(name_);
        __Ownable_init(owner_);

        _mint(owner_, TOTAL_SUPPLY);
    }
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L330-351)
```text
    function test_inv_overflowCap_refundsLt() public {
        (address tokenAddr,) = _launchNoSeed();
        // Crash exchange rate so USD trigger never fires and we can isolate the supply
        // trigger & overflow-cap path.
        lt.setExchangeRate(0.0001 ether);

        uint256 balancePre = lt.balanceOf(trader2);
        // Grossly oversized buy that would attempt to absorb >1B tokens on the curve.
        // Real balance is 750M, so `Router.buy` must cap at 750M and back-calc the LT used.
        uint256 oversizedBuy = 1_000_000_000 ether;

        (uint256 tokensOut, uint256 amountInUsed) = _buy(tokenAddr, trader2, oversizedBuy);

        assertTrue(bonding.isGraduated(tokenAddr), "graduated on capped buy");
        assertTrue(amountInUsed < oversizedBuy, "buy must be capped below oversized request");
        assertEq(tokensOut, CURVE_SUPPLY, "tokensOut must equal remaining real supply");

        // `bonding.buy` pulls only `amountInUsed` from trader2 (via Router → pair + fees).
        uint256 balancePost = lt.balanceOf(trader2);
        uint256 ltConsumed = balancePre + oversizedBuy - balancePost;
        assertEq(ltConsumed, amountInUsed, "trader should only pay `amountInUsed`, not the requested amount");
    }
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L353-366)
```text
    // ─── 8. Virtual reserve invariant (tokenBalance < tokenReserve) ──────

    /// @dev Production seeding (`virtualReserveToken = totalSupply`,
    ///      `realTokenAmount = curveSupply = 75% * totalSupply`) makes
    ///      `pair.tokenBalance() < pair.tokenReserve()` a hard property at
    ///      every state of the curve. This invariant is what makes the
    ///      `cappedReserveToken == 0` branch in `Router._computeBuy`
    ///      unreachable; if it ever ceased to hold, that branch would
    ///      revert with `OverflowCapDegenerate` rather than over-pay.
    function test_inv_virtualReserveAlwaysExceedsRealBalance() public {
        (address tokenAddr, address pairAddr) = _launchNoSeed();

        // Right after launch.
        assertTrue(IPair(pairAddr).tokenBalance() < _reserve0(pairAddr), "post-launch invariant");
```

**File:** packages/contracts/src/Zap.sol (L366-377)
```text
        // Refund LT we minted but the curve didn't consume. In the
        // floor-bump branch with supply-tight this is the meaningful
        // overshoot; on the dust-cap branch it's at most sub-wei from
        // `_computeBuy`'s round-up; on the non-cap and post-graduation
        // branches it's identically zero (`amountInUsed == ltMinted` by
        // construction). Sent to `msg.sender` — `_buyInternal` is
        // `nonReentrant`, mirroring the safe-transfer-at-end-of-flow
        // pattern used for the USDC refund below.
        uint256 ltExcess = ltMinted - amountInUsed;
        if (ltExcess > 0) {
            IERC20(lt).safeTransfer(msg.sender, ltExcess);
        }
```

**File:** docs/contracts-scope.md (L71-71)
```markdown
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```
