## Title
BandwidthManager.purchase() has no `onPostRequestTimeout` refund path — buyer's fee-token payment is permanently lost if the cross-chain credit message is never delivered or is rejected by pallet-bandwidth - (File: `evm/src/apps/BandwidthManager.sol`)

### Summary
`BandwidthManager.purchase()` pulls the buyer's fee token locally and dispatches a `BandwidthPurchaseMsg` to `pallet-bandwidth` on Hyperbridge to credit the bandwidth bucket, but the contract implements no `onPostRequestTimeout` handler at all. Every other Hyperbridge token app that debits a user locally in exchange for a cross-chain credit (`HyperFungibleToken`, `WrappedHyperFungibleToken`) implements a symmetric `onPostRequestTimeout` that re-mints/unlocks the debited funds back to the sender if the message is never delivered. `BandwidthManager` skips this refund step entirely, mirroring the Illuminate H-11 pattern where funds are pulled from the caller but the corresponding credit-back step is missing from the code path.

### Finding Description
In `purchase()`, the contract debits the buyer's fee token immediately: [1](#0-0) 

The dispatch is built with `timeout: 0`: [2](#0-1) 

`BandwidthManager` only implements `onAccept` (for governance messages such as `SetTiers`/`Withdraw` coming back from `pallet-bandwidth`): [3](#0-2) 

There is no `onPostRequestTimeout` override anywhere in the contract (confirmed via a repo-wide search for `onAccept`/`onPostRequestTimeout` implementations — `BandwidthManager.sol` only defines `onAccept`), unlike the symmetric fungible-token apps which always pair a debit with a refund-on-timeout handler, e.g.: [4](#0-3) [5](#0-4) 

Because `HyperApp` timeouts are dispatched by the ISMP host back to the *source* contract's `onPostRequestTimeout` (as documented for HFT/WHFT), any Hyperbridge app that dispatches a `DispatchPost` after debiting a user must implement this hook to make the user whole if the request is never delivered/executed on the destination (relayer never submits it, challenge period expires without proof, or `pallet-bandwidth`'s `on_accept` reverts for a reason not caught client-side, such as a tier or `AppKey` mismatch between the EVM-side `tierPrice` map and the pallet's own tier state). Since `BandwidthManager` inherits `HyperApp` but never overrides `onPostRequestTimeout`, any timeout delivered against this contract is either a no-op (base `HyperApp` default) or reverts — in neither case is the buyer's fee token ever returned.

### Impact Explanation
This is the same fund-loss class as Illuminate H-11: the user's payment/token is taken (`safeTransferFrom`), and the compensating credit-or-refund step that should exist for the failure path is simply absent from the contract. Any bandwidth purchase whose cross-chain message fails to be honored by `pallet-bandwidth` (undelivered, expired proof, tier/app mismatch, pallet-side validation failure) permanently strands the buyer's fee tokens inside `BandwidthManager` with no code path to reclaim them — a concrete, permanent freezing/loss of funds reachable by any unprivileged bandwidth purchaser via a single `purchase()` call.

### Likelihood Explanation
`purchase()` is a fully permissionless, single-transaction entry point available to any bandwidth buyer. The `timeout: 0` on the dispatch, combined with the complete absence of a timeout handler, makes this reachable without any privileged or adversarial actor — it only requires the cross-chain message to fail to be honored (relayer non-delivery, or a validation mismatch between the EVM-side tier check and `pallet-bandwidth`'s own state, which is plausible since tier state is independently mirrored on both sides via `SetTiers` governance messages that could fall out of sync).

### Recommendation
Add an `onPostRequestTimeout(PostRequestTimeout memory incoming)` override to `BandwidthManager` that decodes the original `BandwidthPurchaseMsg`/payer context and refunds the fee token amount to the original purchaser, mirroring the refund pattern used in `HyperFungibleToken.onPostRequestTimeout` and `WrappedHyperFungibleToken.onPostRequestTimeout`. Alternatively/additionally, set a non-zero `timeout` on the `DispatchPost` in `purchase()` so failed deliveries can actually trigger this refund path instead of remaining pending indefinitely.

### Proof of Concept
1. Buyer calls `purchase(app, tier, months, chain)`; `amount` of fee token is pulled from buyer into `BandwidthManager` [6](#0-5) .
2. The `DispatchPost` to `pallet-bandwidth` is created with `timeout: 0` and dispatched [2](#0-1) .
3. `pallet-bandwidth`'s `on_accept` fails to credit the bucket (e.g., due to a stale/unsynced tier, a relayer that never submits the proof, or destination-side validation failure) — the ISMP message is never successfully processed on the destination.
4. Because `BandwidthManager` has no `onPostRequestTimeout` override, there is no code path in this contract that can ever return `amount` of fee token to the original buyer.
5. The buyer's funds remain permanently stuck in `BandwidthManager` with no bandwidth credited and no refund possible — the direct analog of Illuminate H-11's "funds transferred, no compensating token issued."

### Citations

**File:** evm/src/apps/BandwidthManager.sol (L170-188)
```text
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

**File:** evm/src/apps/BandwidthManager.sol (L208-232)
```text
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
        } else {
            revert UnauthorizedAction();
        }
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-282)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L321-326)
```text
    function onPostRequestTimeout(PostRequestTimeout memory incoming) public virtual override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```
