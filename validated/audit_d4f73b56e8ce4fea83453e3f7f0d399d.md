### Title
Attacker-donated Token balance permanently bricks the curve's overflow-cap buy path, freezing remaining curve supply and blocking supply-trigger graduation - (File: `packages/contracts/src/Router.sol`)

### Summary
`Router._computeBuy` caps the last curve-emptying buy by comparing a purely reserve-derived (`stored`) `tokensOut` against the pair's *live* `IERC20.balanceOf` (`pair.tokenBalance()`), then re-derives `amountInUsed` from `cappedReserveToken = reserveToken - tokensOut`. Because any unprivileged holder of the launched `Token` can `transfer` it directly into the `Pair` contract, they can inflate the live balance read by `tokenBalance()` independently of the stored virtual `reserveToken`, closing (or inverting) the gap the cap math depends on. When the curve later reaches the point that would normally trigger the overflow cap, `cappedReserveToken` computes to `0` (explicit `OverflowCapDegenerate()` revert) or underflows (Solidity 0.8 arithmetic panic) — and this state is persistent, so every subsequent attempt to execute that capping buy reverts identically.

### Finding Description
`Router._computeBuy` (packages/contracts/src/Router.sol, `_computeBuy`) is: [1](#0-0) 

The cap only activates when the reserve-derived `tokensOut` exceeds the pair's *live* real balance:
```
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;
    uint256 cappedReserveToken = reserveToken - tokensOut;
    if (cappedReserveToken == 0) revert OverflowCapDegenerate();
    ...
}
```
`pair.tokenBalance()` is a live `balanceOf` read: [2](#0-1) 

whereas `reserveToken`/`reserveAsset` are the *stored* `Pool` values, mutated only by `Pair.swap` (called exclusively through `BONDING_ROLE`-gated `Router`): [3](#0-2) 

By design, on every ordinary buy both the stored `reserveToken` and the live real balance decrease by the same `tokensOut`, so the gap `G = reserveToken - realBalance` stays constant at the launch-time value (`250M`, per the virtual-reserve design documented in `docs/contracts-scope.md`). At the exact moment the cap triggers (i.e., the last capping buy that drains the remaining real balance), `cappedReserveToken` reduces algebraically to that same gap `G`:
```
cappedReserveToken = reserveToken - tokensOut  (tokensOut == realBalance at that instant)
                    = reserveToken - realBalance
                    = G
```
The launch-time invariant relied on for this to stay non-zero is `pair.tokenBalance() < reserve0` at every state, explicitly noted as depending only on production seeding ratios: [4](#0-3) 

That invariant assumes no external party can move the live `tokenBalance()` independently of the stored reserve. But any address holding the launched `Token` — obtainable via an ordinary `Zap.buy` — can call the standard ERC20 `transfer(pair, amount)` directly, since `Token` is an unrestricted `ERC20Upgradeable`: [5](#0-4) 

This donation increases `realBalance` without touching stored `reserveToken`, shrinking `G` by the donated amount. If enough is donated to drive `G` to `0` (or below), the pair permanently loses the ability to execute its final capping buy: every future attempt at the buy that would trigger the cap branch reverts with `OverflowCapDegenerate()` (or an arithmetic panic if `G` goes negative). This is not a one-off revert — the gap `G` is persistent pair state, so the condition recurs identically on every subsequent attempt, matching the CVE's "hang or frequently repeatable crash" DOS class.

The protocol's own donation-resistance design only guards the *graduation* accounting (`_prepareGraduationLiquidity` burns donated tokens at graduation time) and the supply-trigger check (`canGraduate`'s `tokenBalance() == 0` test, which donations can only push further from zero, never satisfy). Neither of these defenses is invoked from `Router._computeBuy`/`Router.buy`, so the mid-curve cap-math bug is untouched by them.

### Impact Explanation
For a token whose bonding curve never crosses the USD graduation threshold (explicitly acknowledged as a real, expected scenario — "flat/bear markets where $9K is never reached" per `docs/contracts-scope.md`), the *only* path to completing the sale of the last chunk of real curve tokens and reaching the supply-trigger graduation is the capping buy in `Router._computeBuy`. Once an attacker (who need only be a normal token holder) donates enough of the launched `Token` to the `Pair` to zero out the gap `G`, that capping buy permanently reverts. Consequences:
- The remaining real curve tokens become permanently unsellable/un-buyable through the intended cap path — trader funds attempting that final buy revert every time.
- The token can never reach the supply-based graduation trigger, and if the LT's price never appreciates enough for the USD trigger, the token is permanently stuck in `Lifecycle.Curve`, unable to graduate to the HyperSwap V2 pool, freezing the protocol-held `250M` LP reserve and any raised LT indefinitely on `Bonding`/the curve `Pair`.
- This is a permanent freezing of funds (creator's raised LT, remaining curve token supply, and the LP path) rather than a temporary griefing — satisfying the Medium/High bar.

### Likelihood Explanation
The attack requires only:
1. Acquiring some amount of the launched `Token` via a normal `Zap.buy` (any unprivileged trader can do this).
2. A single unrestricted ERC20 `transfer` of that `Token` to the `Pair` address, which is public and discoverable via `Factory`/`Bonding.getTokenInfo`.

No special privileges, timing races, or governance access are needed — any trader, including the token's own creator (e.g., wishing to prevent competitors from ever graduating, or to strand a chosen token permanently on the curve), can execute it deterministically. The exact donation size needed is computable off-chain from public `Pair.getReserves()`/`tokenBalance()` reads.

### Recommendation
Decouple the overflow-cap math in `Router._computeBuy` from the pair's live `balanceOf`-based `tokenBalance()`. Track "real tokens remaining on the curve" as explicit stored state (mutated only by `Router`-gated `swap`/`mint`, mirroring `reserveToken`/`reserveAsset`) rather than deriving it from a value that any external ERC20 transfer can perturb. Alternatively, have `_computeBuy` compute the cap purely from the invariant `realBalance = reserveToken - LAUNCH_GAP` (a constant known at launch) instead of reading live balance, and separately sweep/burn any donated `Token` balance before it can influence buy-cap arithmetic — mirroring the donation-burn already done for `_prepareGraduationLiquidity`.

### Proof of Concept
1. `Zap.createToken(...)` launches a token; curve seeds with `reserveToken = 1e9 ether`, real `tokenBalance() = 750_000_000 ether` (gap `G = 250_000_000 ether`).
2. Attacker (any address) calls `Zap.buy` to acquire some `Token`, or simply uses tokens obtained from a prior buy.
3. Attacker calls `Token.transfer(pairAddr, 250_000_000 ether)` (a plain ERC20 transfer, no role required), driving `pair.tokenBalance()` up so that `G = reserveToken - tokenBalance()` becomes `0`.
4. Any subsequent trader submits a buy large enough that `Router._computeBuy`'s uncapped `tokensOut` would exceed the (still-live) `realBalance` — the natural "curve-emptying" buy.
5. `_computeBuy` sets `tokensOut = realBalance`, computes `cappedReserveToken = reserveToken - tokensOut == 0`, and reverts with `OverflowCapDegenerate()` (as defined in `Router.sol` line 29) — deterministically, on every subsequent attempt, since `G` remains `0` until further state changes. The curve's final sellout — and hence supply-trigger graduation — is permanently blocked for as long as the USD trigger is not independently satisfied.

### Citations

**File:** packages/contracts/src/Router.sol (L127-148)
```text
    function _computeBuy(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 amountInUsed, uint256 tokensOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        amountInUsed = amountIn;

        uint256 newReserveAsset = reserveAsset + amountInUsed;
        tokensOut = reserveToken - (k / newReserveAsset);

        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
    }
```

**File:** packages/contracts/src/Pair.sol (L65-79)
```text
    function swap(
        uint256 tokenIn,
        uint256 tokenOut,
        uint256 assetIn,
        uint256 assetOut
    ) external onlyRouter returns (bool) {
        uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
        uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
        if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();

        _pool.tokenReserve = newTokenReserve;
        _pool.assetReserve = newAssetReserve;
        emit Swap(tokenIn, tokenOut, assetIn, assetOut);
        return true;
    }
```

**File:** packages/contracts/src/Pair.sol (L103-105)
```text
    function tokenBalance() external view returns (uint256) {
        return IERC20(launchedToken).balanceOf(address(this));
    }
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L353-377)
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

        // After a series of buys the property must continue to hold while
        // the curve is still trading.
        for (uint256 i = 0; i < 10; i++) {
            if (!bonding.isTrading(tokenAddr)) break;
            _buy(tokenAddr, trader, 100 ether);
            if (bonding.isTrading(tokenAddr)) {
                assertTrue(IPair(pairAddr).tokenBalance() < _reserve0(pairAddr), "invariant must hold after every buy");
            }
        }
    }
```

**File:** packages/contracts/src/Token.sol (L18-44)
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

    /// @notice Burn from any address. Owner only, no approval required.
    function burn(
        address from,
        uint256 amount
    ) external onlyOwner {
        _burn(from, amount);
    }
}
```
