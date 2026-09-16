## Title
`BandwidthManager.onAccept` native-token `Withdraw` governance action always reverts because the contract cannot receive ETH — ([File: evm/src/apps/BandwidthManager.sol])

### Summary
`BandwidthManager` supports a governance `Withdraw` action delivered via `onAccept` from `pallet-bandwidth` that can target either the fee-token (ERC20) or the native token (`token == address(0)`) [1](#0-0) . When the native-token branch is taken, it does a low-level `call{value: w.amount}` to push ETH out of the contract's own balance [2](#0-1) . However, `BandwidthManager` has no `receive()`/`fallback()` and no `payable` entry point anywhere — `purchase()` only moves the ERC20 fee token via `safeTransferFrom` and `IDispatcher(_host).dispatch(...)` is called without `value` [3](#0-2) . The contract therefore can never accumulate a native-token balance, and any `Withdraw` message with `token == address(0)` and `amount > 0` will unconditionally revert on the `call`, since the check `if (!sent) revert InsufficientNativeToken();` catches the failed transfer [4](#0-3) . This mirrors the reported `TemporalGovernor` bug class: a legitimate, correctly-formed governance/relayed instruction targeting a contract with no way to hold native value, causing execution to permanently revert.

### Finding Description
The `Withdrawal` struct and its handling path are explicitly designed to support recovering native-currency balances (`token` is "named explicitly so stale fee-token balances ... can still be drained", implying symmetric handling for native token) [1](#0-0) . `onAccept` is invoked by the `IsmpHost` (via `onlyHost`) whenever a relayer delivers a proven POST request from `pallet-bandwidth`, and the first payload byte selects `OnAcceptActions.Withdraw` [5](#0-4) . Since `BandwidthManager` inherits only `HyperApp`, `ERC165`, and `Ownable` — none of which define a `receive()`/payable fallback — and none of its own functions are `payable`, the contract's ETH balance is always `0`. Any relayed `Withdraw` action with `token == address(0)` therefore executes `w.beneficiary.call{value: w.amount}("")` against an empty balance, which fails and reverts the whole `onAccept` transaction.

### Impact Explanation
Any relayed message from `pallet-bandwidth` instructing a native-token withdrawal can never be delivered/executed: the relayer's delivery transaction will always revert, permanently blocking that message from settling. This is a route that is structurally unable to deliver a class of governance message, matching "a route unable to deliver messages" — the pallet-side logic assumes native withdrawal is a supported, executable action, but the EVM-side contract can never satisfy it.

### Likelihood Explanation
This triggers deterministically any time `pallet-bandwidth` issues a `Withdraw` action with `token == address(0)`, which the struct/enum design clearly anticipates as a supported code path. No attacker action is required — it is a latent, always-reachable break in the intended governance flow the moment that message type is used.

### Recommendation
Add a `receive() external payable {}` to `BandwidthManager` (as already done in `IntentGatewayV2`, `CallDispatcher`, `HostManager`, and the `WrappedHyperFungibleToken` variants) [6](#0-5) , and/or ensure the contract actually accrues native balance (e.g., accept `msg.value` on `purchase()` if native fee payment is intended, or restrict `Withdraw` to the fee token only if native withdrawal was never meant to be supported).

### Proof of Concept
1. Deploy `BandwidthManager`, set `_host`.
2. Have the host relay an `onAccept` call with `request.source == hyperbridge()` and body `abi.encodePacked(uint8(OnAcceptActions.Withdraw), abi.encode(Withdrawal({token: address(0), beneficiary: someEOA, amount: 1 ether})))`.
3. Observe `onAccept` reverts with `InsufficientNativeToken` because `address(BandwidthManager).balance == 0` (it has no `receive()`/payable path to ever hold ETH), demonstrating the native-token withdrawal path can never succeed. [2](#0-1)

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

**File:** evm/src/apps/BandwidthManager.sol (L203-228)
```text
    /// @notice Inbound governance from `pallet-bandwidth`. The first
    /// body byte selects `OnAcceptActions`; the remainder is the
    /// action's ABI-encoded payload.
    /// @dev Only the configured host may invoke (`onlyHost`); the
    /// request's `source` must additionally equal hyperbridge.
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        PostRequest calldata request = incoming.request;

        if (!request.source.equals(IDispatcher(_host).hyperbridge())) revert UnauthorizedAction();

        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.SetTiers) {
            Tier[] memory updates = abi.decode(request.body[1:], (Tier[]));
            for (uint256 i = 0; i < updates.length; i++) {
                tierPrice[updates[i].tier] = updates[i].price;
                emit TierSet(updates[i].tier, updates[i].price);
            }
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

**File:** evm/src/apps/IntentGatewayV2.sol (L77-82)
```text
    /**
     * @dev Allows the contract to receive native tokens (ETH/DOT/etc).
     * Required for escrow deposits with native tokens and for receiving
     * swept balances from the CallDispatcher.
     */
    receive() external payable {}
```
