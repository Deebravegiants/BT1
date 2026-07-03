Audit Report

## Title
Missing Fee Initialization in `addSupportedToken` Allows Zero-Fee Token Deposits - (File: contracts/pools/RSETHPool.sol)

## Summary
`addSupportedToken` sets the oracle and bridge for a new token but never initializes `tokenFeeBps[token]`, leaving it at the Solidity default of `0`. Any depositor who calls `deposit(token, amount, referralId)` before the admin separately calls `setTokenFeeBps` pays zero protocol fees and receives more wrsETH than the protocol intends, permanently depriving the treasury of fee yield for all deposits made in that window.

## Finding Description
`tokenFeeBps` is declared at [1](#0-0)  as a per-token fee mapping. `addSupportedToken` (L637–656) writes `supportedTokenOracle[token]` and `tokenBridge[token]` but never writes `tokenFeeBps[token]`: [2](#0-1) 

The fee calculation in `viewSwapRsETHAmountAndFee(uint256, address)` reads this mapping directly: [3](#0-2) 

Because the mapping is `0`, `fee = amount * 0 / 10_000 = 0` and `amountAfterFee = amount`, so the depositor receives wrsETH calculated on the full token amount. The `deposit` function accumulates `feeEarnedInToken[token] += fee` (which is `+= 0`) and transfers the inflated wrsETH amount to the caller: [4](#0-3) 

The only remedy is a separate `setTokenFeeBps` call gated by `DEFAULT_ADMIN_ROLE`: [5](#0-4) 

There is no on-chain enforcement requiring this call to happen atomically with or before any deposit. The `onlySupportedToken` modifier only checks that `supportedTokenOracle[token] != address(0)`, which is satisfied immediately after `addSupportedToken` executes, so deposits are open the moment the timelock fires.

## Impact Explanation
**High — Theft of unclaimed yield.** The protocol is designed to retain a fee (in token form) from every token deposit and accumulate it in `feeEarnedInToken[token]` for withdrawal to the treasury. With `tokenFeeBps[token] == 0`, the full token amount is used to compute `rsETHAmount`, meaning the pool transfers out more wrsETH than it should. The fee yield that should have accrued to the treasury is instead captured by depositors as excess wrsETH. These fees are permanently lost for every deposit made before `setTokenFeeBps` is called; they cannot be recovered retroactively.

## Likelihood Explanation
`addSupportedToken` is gated by `TIMELOCK_ROLE`, making the pending transaction publicly visible on-chain before execution. A watching depositor can prepare a deposit transaction and submit it immediately after the timelock executes, before any `setTokenFeeBps` transaction is mined. Even without deliberate front-running, any ordinary depositor who interacts with the pool in the gap between the two admin transactions pays zero fees. The window persists until the admin issues a second transaction, which may span multiple blocks or longer.

## Recommendation
Add a `_feeBps` parameter to `addSupportedToken` and set `tokenFeeBps[token] = _feeBps` atomically within the same call, mirroring how `feeBps` is passed to `initialize`. Enforce `_feeBps <= 10_000` with the same guard used in `setTokenFeeBps`. This eliminates the uninitialized window entirely.

## Proof of Concept
1. Admin calls `addSupportedToken(token, oracle, bridge)` via the timelock. `tokenFeeBps[token]` is `0`.
2. Depositor (who observed the pending timelock tx) calls `deposit(token, largeAmount, "")` immediately after execution.
3. Inside `deposit`, `viewSwapRsETHAmountAndFee(largeAmount, token)` computes:
   - `feeBpsForToken = tokenFeeBps[token]` → `0`
   - `fee = largeAmount * 0 / 10_000` → `0`
   - `amountAfterFee = largeAmount`
   - `rsETHAmount = largeAmount * tokenToETHRate / rsETHToETHrate` (full amount, no fee deduction)
4. Pool transfers `rsETHAmount` wrsETH to depositor; `feeEarnedInToken[token]` remains `0`.
5. Admin later calls `setTokenFeeBps(token, intendedFeeBps)`, but all prior deposits have already bypassed the fee with no recourse.

**Foundry test sketch:**
```solidity
function test_zeroFeeOnNewToken() public {
    // addSupportedToken with no subsequent setTokenFeeBps
    vm.prank(timelockRole);
    pool.addSupportedToken(token, oracle, bridge);

    uint256 amount = 1e18;
    deal(token, attacker, amount);
    vm.startPrank(attacker);
    IERC20(token).approve(address(pool), amount);
    pool.deposit(token, amount, "");
    vm.stopPrank();

    // Fee earned should be > 0 if fee was set, but it is 0
    assertEq(pool.feeEarnedInToken(token), 0);
    // Depositor received rsETH calculated on full amount (no fee deducted)
}
```

### Citations

**File:** contracts/pools/RSETHPool.sol (L87-88)
```text
    /// @dev Mapping of token to fee basis points
    mapping(address token => uint256 feeBps) public tokenFeeBps;
```

**File:** contracts/pools/RSETHPool.sol (L298-302)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPool.sol (L335-337)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPool.sol (L583-594)
```text
    function setTokenFeeBps(
        address token,
        uint256 _feeBps
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        onlySupportedToken(token)
    {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        tokenFeeBps[token] = _feeBps;
        emit TokenFeeBpsSet(token, _feeBps);
    }
```

**File:** contracts/pools/RSETHPool.sol (L637-656)
```text
    function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        UtilLib.checkNonZeroAddress(oracle);
        UtilLib.checkNonZeroAddress(bridge);

        if (supportedTokenOracle[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (tokenBridge[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;
        tokenBridge[token] = bridge;

        emit AddSupportedToken(token, oracle, bridge);
    }
```
