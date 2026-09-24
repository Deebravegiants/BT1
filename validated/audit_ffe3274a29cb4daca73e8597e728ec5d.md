### Title
Zap.sol has no sweep/rescue function — any Token, LT, or USDC stuck in the contract is permanently locked - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap` is the sole user-facing entry point that custodies USDC, LT, and launched `Token` balances mid-transaction (`_buyInternal`/`_sellInternal`, `_buyOnCurve`, `_sellOnCurve`, `_swapOnUniswapV2`) [1](#0-0) . Unlike `Bonding` (which has `_sweepLTToOwner` for graduation-residue LT) and `FeeVault` (which has permissionless `sweepDonations`), `Zap` exposes no owner-only or permissionless sweep function for any ERC20 it may end up holding. Any USDC, LT, or launched Token that lands on `Zap`'s balance outside the exact code paths that already account for it — e.g. a stray direct `transfer()` from a third-party wallet, or dust from `SafeERC20`/rounding edge cases not covered by the existing refund logic — is permanently unrecoverable.

### Finding Description
The report's underlying bug class is: contracts that legitimately hold or can accidentally receive value (ETH/ERC20) but provide no rescue mechanism, causing permanent loss of user/protocol funds. In alt.fun's shape, the codebase is otherwise disciplined about this:

- `FeeVault` explicitly implements `sweepDonations()`, permissionless, to recover stray USDC donations [2](#0-1) .
- `Bonding._sweepLTToOwner` recovers LT residue left over from graduation rebalancing/donations, and `_prepareGraduationLiquidity` explicitly burns donated Token dust [3](#0-2) .
- `_seedUniswapV2Direct` even calls `IUniswapV2Pair(pair).skim(address(this))` specifically to pull pre-seed donations out of the pair before they pollute the LP ratio, routing them to `Bonding` where they can later be rescued [4](#0-3) .

`Zap`, however, has zero such mechanism. Grepping its full source for `sweep`/`rescue`/`skim` returns no rescue-style function — only unrelated `onlyOwner` matches (e.g. `_authorizeUpgrade`, fee setters) and comments describing FeeVault's own sweep. `Zap` is `ReentrancyGuard`-protected and `Ownable2StepUpgradeable`, but no owner path exists to reclaim ERC20 balances from `Zap` itself. Every value-moving function in `Zap` (`_buyInternal`, `_sellInternal`, `_buyOnCurve`, `_sellOnCurve`, `_swapOnUniswapV2`) assumes the only tokens sitting on `Zap`'s balance are the ones it minted/received in the current call, and unconditionally forwards computed amounts — it never reconciles against `balanceOf(address(this))`. Consequently:

- A stranger directly `transfer()`-ing USDC, a launched `Token`, or an LT to `Zap`'s address is permanently locked — there is no function in `Zap`'s ABI that can move it out.
- Any future rounding edge case in the buy/sell refund math (`ltExcess`, `usdcLeft`, `feeRefund` in `_buyInternal`) that doesn't fully net to zero leaves dust stranded with no recovery path, unlike the equivalent LT dust in `Bonding` which is swept by `_sweepLTToOwner`.

### Impact Explanation
This is a direct, permanent freezing-of-funds bug class matching the source report exactly (Comet/Bulker locked ETH due to missing sweep function). Any USDC, Token, or LT that lands on `Zap` outside its exact accounted-for flows is unrecoverable forever — no owner function, no permissionless sweep, no upgrade-triggered rescue path exists. Given `Zap` is the single most trafficked contract in the protocol (every buy/sell/createToken call), and third parties can trivially `transfer()` any of USDC/LT/Token to its address at any time, this is a realistic, low-cost griefing/loss vector with unbounded value at risk over the contract's lifetime.

### Likelihood Explanation
High reachability: any unprivileged wallet can call `IERC20(usdc).transfer(zapAddress, amount)` (or the same for any launched `Token` or LT) at zero cost beyond gas and normal ERC20 approval. No special permissions, timing, or MEV positioning is required. The team's own pattern elsewhere in the codebase (`FeeVault.sweepDonations`, `Bonding._sweepLTToOwner`) shows this exact risk was recognized and mitigated for other contracts but was omitted for `Zap`.

### Recommendation
Add an owner-gated (or permissionless-to-owner, mirroring `FeeVault.sweepDonations`) `sweep(address token, address to)` function on `Zap` that transfers any ERC20 balance held by the contract to a designated recipient (e.g., the protocol owner or `FeeVault`), guarded against reentrancy and restricted from being called mid another external call. If `Zap` is intended to never hold ETH, consider omitting a `receive()`/`fallback()` entirely (it currently has none based on the reviewed interface) to avoid the ETH-analog of this issue as well.

### Proof of Concept
1. Deploy the protocol normally; `Zap` is live and processing buys/sells.
2. Any address (attacker, or an honest user who fat-fingers a transfer) calls `usdc.transfer(address(zap), 1_000e6)` directly (not via `Zap.buy`).
3. Inspect `Zap`'s ABI/source (`packages/contracts/src/Zap.sol`) — there is no `sweep`, `rescue`, `recoverERC20`, or equivalent function reachable by the owner or anyone else.
4. The 1,000 USDC (or LT, or launched Token, sent the same way) sits on `Zap`'s balance forever; no transaction can move it out because every `Zap` function that transfers ERC20 does so against internally computed amounts, never against `balanceOf(address(this))` minus expected in-flight amounts.

### Citations

**File:** packages/contracts/src/Zap.sol (L239-240)
```text
    function _buyInternal(
        address tokenAddress,
```

**File:** packages/contracts/test/FeeVault.t.sol (L343-353)
```text
    function test_sweepDonations_permissionless() public {
        usdc.mint(address(vault), 50 ether);

        // A stranger triggers the sweep; funds still go to the admin-set feeTo.
        vm.prank(stranger);
        uint256 swept = vault.sweepDonations();

        assertEq(swept, 50 ether);
        assertEq(usdc.balanceOf(feeTo), 50 ether);
        assertEq(usdc.balanceOf(stranger), 0);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1042-1052)
```text
    function _sweepLTToOwner(
        address lt,
        uint256 keep
    ) internal {
        uint256 bal = IERC20(lt).balanceOf(address(this));
        if (bal <= keep) return;
        uint256 amount = bal - keep;
        address recipient = owner();
        IERC20(lt).safeTransfer(recipient, amount);
        emit LTRescued(lt, recipient, amount);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1209-1215)
```text
        // Regime 2 — pull any donation pre-seed into this contract so it
        // doesn't pollute the post-swap ratio. Routed to `address(this)`
        // (NOT `lpLock`) so donated TOKEN can be burned and donated LT
        // can be swept to the owner via `_sweepLTToOwner` — `LPLock` has
        // no rescue path, so anything sent there is permanently stuck.
        // No-op on a freshly-created pair (balance == reserves == 0).
        IUniswapV2Pair(pair).skim(address(this));
```
