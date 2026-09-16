### Title
BandwidthManager governance Withdraw can only ever revert for native token because the contract has no `receive()`/`fallback()` and never accepts `msg.value` - ([File: evm/src/apps/BandwidthManager.sol])

### Summary
`BandwidthManager` implements an `onAccept` governance action `Withdraw` that, when `w.token == address(0)`, attempts to send native ETH out of the contract via a low-level `call{value: w.amount}` [1](#0-0) . However, `BandwidthManager` has no `receive()` or `fallback()` function, and its only fund-accepting entrypoint, `purchase()`, exclusively pulls the fee token via `safeTransferFrom` — it never accepts or forwards native ETH [2](#0-1) . This mirrors the reported TimeLock pattern: the contract is coded with the ability to transfer ETH out, but has no legitimate path to receive ETH in, so this withdrawal path is effectively dead / permanently unusable via `pallet-bandwidth` governance.

### Finding Description
The contract's design intent is clear from the `Withdrawal` struct's comment: "recovers `amount` of `token` to `beneficiary` ... `token` is named explicitly so stale fee-token balances after a host-side swap can still be drained" [3](#0-2) . This strongly implies the contract is expected to hold and later disburse balances of arbitrary tokens, including native ETH (the `token == address(0)` branch is native-token-specific code, not incidental).

Yet nowhere in `BandwidthManager` is there a `payable` function, `receive()`, or `fallback()` to let ETH enter the contract:
- `purchase()` is not `payable` and only moves the ERC20 fee token [4](#0-3) .
- `IDispatcher(_host).dispatch(...)` is invoked with `fee: 0` and no `{value: ...}`, so no ETH flows through the dispatch call either [5](#0-4) .
- `onAccept` itself is not `payable` [6](#0-5) .

Consequently, `address(this).balance` for `BandwidthManager` can never be intentionally funded through the contract's own logic. If `pallet-bandwidth` governance ever issues a `Withdraw` action with `token == address(0)` and `amount > 0` (the branch exists specifically to support this), the transfer `w.beneficiary.call{value: w.amount}("")` will revert due to insufficient balance, and the whole `onAccept` call reverts with `InsufficientNativeToken` [7](#0-6) . Since `onAccept` is the sole path by which this cross-chain governance message is delivered and processed (`onlyHost`), and there is no retry/alternate mechanism shown in this contract, this governance instruction can never be fulfilled as coded, and any accompanying `TierSet` batching logic sharing the same delivery path is not affected only because it's a separate discriminant — but the native-withdraw branch is permanently broken by construction.

This is directly analogous to the reported `TimeLock` issue: a contract is built to move ETH out via `call{value: ...}` but the codebase gives it no way to legitimately hold ETH, making that code path either dead on arrival or a permanent freeze/DoS vector against a governance action that the protocol explicitly designed pallet-bandwidth to be able to execute.

### Impact Explanation
The impact is a permanently non-functional governance instruction: `pallet-bandwidth` (the counterparty ISMP module authorized to control `BandwidthManager` via cross-chain governance) cannot ever execute a native-ETH withdrawal through this contract, because the contract can never legitimately be funded with ETH in the first place. This is a "route unable to deliver messages"/broken protocol-function class of issue rather than a fee-token loss — the fee-token withdraw branch is unaffected since ERC20 transfers do not depend on `msg.value`. Any native ETH that reaches the contract only by forced means (e.g., `selfdestruct` targeting, or miner/validator payments) would be undrainable up to the amount actually present, and any governance withdraw expecting to reclaim it in full will revert if it exceeds that forced balance, since the branch has no legitimate funding mechanism to true it up.

### Likelihood Explanation
Likelihood of the withdraw revert path being hit is moderate-to-low in practice: it only matters if/when `pallet-bandwidth` governance issues a `Withdraw` with `token == address(0)`, which the code was explicitly written to support. Given there is no legitimate way to fund the contract's native balance, this scenario is essentially guaranteed to fail whenever attempted, indicating a genuine dead/broken code path rather than a hypothetical edge case.

### Recommendation
Add a `receive() external payable {}` (and/or a `payable` variant of `purchase()`/an explicit native-fund deposit function) to `BandwidthManager` so the native-token branch of the `Withdraw` governance action has a legitimate way to be funded and executed, consistent with the `Withdrawal` struct's stated intent to recover both ERC20 and native balances.

### Proof of Concept
1. `pallet-bandwidth` governance sends an ISMP POST that decodes to `OnAcceptActions.Withdraw` with `Withdrawal{ token: address(0), beneficiary: X, amount: N }`.
2. The relayer delivers this to `BandwidthManager.onAccept`, entering the `else if (action == OnAcceptActions.Withdraw)` branch [8](#0-7) .
3. Since `BandwidthManager` has never received any ETH (no `receive()`/`fallback()`/payable path exists anywhere in the contract), `address(this).balance == 0 < N`.
4. `w.beneficiary.call{value: w.amount}("")` fails, `sent == false`, and the call reverts with `InsufficientNativeToken()`, permanently blocking this governance instruction from ever succeeding as designed.

### Citations

**File:** evm/src/apps/BandwidthManager.sol (L50-57)
```text
/// Payload of a `Withdraw` governance message — recovers `amount` of
/// `token` to `beneficiary`. `token` is named explicitly so stale
/// fee-token balances after a host-side swap can still be drained.
struct Withdrawal {
    address token;
    address beneficiary;
    uint256 amount;
}
```

**File:** evm/src/apps/BandwidthManager.sol (L119-120)
```text
    /// Insufficient native token balance to cover the withdrawal amount.
    error InsufficientNativeToken();
```

**File:** evm/src/apps/BandwidthManager.sol (L153-188)
```text
    function purchase(bytes calldata app, uint256 tier, uint256 months, bytes calldata chain)
        external
        returns (bytes32 commitment)
    {
        if (app.length == 0 || app.length > MAX_APP_LENGTH || chain.length == 0 || months == 0) {
            revert InvalidPurchase();
        }
        uint256 price18d = tierPrice[tier];
        if (price18d == 0) revert UnknownTier();

        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(_host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        uint256 scale = 10 ** (18 - dec);
        if (total18d % scale != 0) revert PriceNotRepresentable();
        uint256 amount = total18d / scale;

        IERC20(feeToken).safeTransferFrom(msg.sender, address(this), amount);

        BandwidthPurchaseMsg memory body = BandwidthPurchaseMsg({
            app: app,
            tier: tier,
            months: months,
            chain: chain
        });

        commitment = IDispatcher(_host).dispatch(
            DispatchPost({
                dest: IDispatcher(_host).hyperbridge(),
                to: PALLET_BANDWIDTH_MODULE_ID,
                body: abi.encode(body),
                timeout: 0,
                fee: 0,
                payer: address(this)
            })
        );
```

**File:** evm/src/apps/BandwidthManager.sol (L208-208)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
```

**File:** evm/src/apps/BandwidthManager.sol (L220-228)
```text
        } else if (action == OnAcceptActions.Withdraw) {
            Withdrawal memory w = abi.decode(request.body[1:], (Withdrawal));
            if (w.token != address(0)) {
                IERC20(w.token).safeTransfer(w.beneficiary, w.amount);
            } else {
                (bool sent,) = w.beneficiary.call{value: w.amount}("");
                if (!sent) revert InsufficientNativeToken();
            }
            emit Withdrawn(w.token, w.beneficiary, w.amount);
```
