### Title
`WrappedHyperFungibleToken.send()` locks the requested amount via `safeTransferFrom` but dispatches the un-adjusted `params.amount`, so fee-on-transfer/deflationary underlying tokens create an escrow shortfall that later causes `onAccept`/`onPostRequestTimeout` to revert on `safeTransfer` — (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` pulls `params.amount` of the underlying ERC20 via `safeTransferFrom` without measuring the actual amount received, then embeds the unadjusted `params.amount` in the cross-chain `Message` that is dispatched to the peer contract on the destination chain. On the receiving side, `onAccept()` (and the symmetric `onPostRequestTimeout()` refund path) unconditionally calls `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` using that same unadjusted amount. This is the exact bug class from the dTRINITY `DLoopCoreBase._deposit()` report: the code assumes the amount requested equals the amount actually escrowed/held, and blindly forwards the requested amount instead of the amount actually received.

### Finding Description
In `send()`: [1](#0-0) 
the ERC20 branch does `IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);` with no balance-before/after check, and then builds and dispatches the message body with `amount: params.amount` unchanged: [2](#0-1) 

If `_underlying` is a fee-on-transfer, rebasing, or otherwise deflationary ERC20 (the contract places no restriction on which token can be configured as `_underlying` — see `configure()`), the contract actually receives less than `params.amount`, yet the dispatched message and the `Sent` event both report the full `params.amount`. This mirrors the `IntentGatewayV2.sol` design elsewhere in the same repo, which explicitly measures balance-before/after and mutates `order.inputs[i].amount` to the *actually received* amount for exactly this reason (see the `placeOrder` fee-on-transfer handling), but `WrappedHyperFungibleToken` has no equivalent correction: [3](#0-2) 

On the destination side (a peer `WrappedHyperFungibleToken` instance wrapping the same underlying, or the same contract processing its own escrow release on `onPostRequestTimeout`), the amount embedded in the message is used verbatim to transfer tokens out: [4](#0-3) [5](#0-4) 

Because the escrow contract on the source side never actually holds `params.amount` of the underlying token (it holds `params.amount` minus the transfer fee), any code path that needs to pay out `message.amount` of the underlying from that contract's balance — most directly the `onPostRequestTimeout` refund path, which runs on the *same* contract/chain that ran `send()` — will attempt to `safeTransfer` more of the underlying than the contract actually holds and revert.

### Impact Explanation
This is a permanent denial-of-service / fund-freezing bug reachable by any unprivileged user who calls `send()` with a fee-on-transfer or deflationary token configured as `_underlying`:
- If the cross-chain POST later times out, `onPostRequestTimeout` tries to refund `message.amount` (the pre-fee amount) but the contract only escrowed the post-fee amount, so the `safeTransfer` reverts and the ISMP timeout handling for that request can never complete — the user's tokens (the reduced amount actually held) become permanently stuck, unable to be refunded.
- Repeated `send()` calls compound the shortfall across the whole pool of escrowed underlying tokens shared by all users of the wrapper, meaning legitimate users transferring a compliant (non-fee) token can also be starved once the contract's real balance falls behind the sum of amounts it has promised via dispatched messages, since the contract has no accounting to distinguish "amount promised" from "amount actually escrowed" per request.
- On the destination side, if the mirrored deployment is also a `WrappedHyperFungibleToken` locking its own underlying pool, the same discrepancy causes `onAccept` calls for other users to revert once the escrow pool is depleted relative to promised amounts, effectively DoS-ing further deliveries.

This matches the "Medium/High, permanent freezing of funds / unable to deliver messages" criteria: the message itself cannot be reliably settled (delivery or timeout-refund reverts), and funds already locked in the contract become unrecoverable for the affected sender.

### Likelihood Explanation
Likelihood depends on `_underlying` being a fee-on-transfer/deflationary token, which is a governance/owner configuration choice (`configure()` sets `_underlying` once). This is not attacker-controlled in the sense of choosing which token is wrapped, but it is fully triggerable by any ordinary unprivileged user calling `send()` once such a token is configured — no special privileges, race conditions, or governance compromise are required to trigger the shortfall or the subsequent revert. Given that "wrap arbitrary existing ERC20 tokens" is the stated purpose of this contract (`@notice Cross-chain wrapper for existing ERC20 tokens`), deployment against a fee-on-transfer token is a realistic, foreseeable scenario, especially since the sibling `IntentGatewayV2.sol` contract in the same codebase explicitly hardens against this exact case, indicating the underlying risk is already known to the team but was not addressed in `WrappedHyperFungibleToken`.

### Recommendation
In `send()`, measure the underlying's balance before and after `safeTransferFrom` (as `IntentGatewayV2.placeOrder` already does) and use the *actually received* delta as `message.amount` in the dispatched body and in the `Sent` event, instead of the raw `params.amount`. Apply the same before/after balance measurement to the WETH-wrapping branch for consistency. This ensures the contract never promises, via the cross-chain message, more of the underlying than it actually escrowed, eliminating the downstream revert-DoS in `onAccept` and `onPostRequestTimeout`.

### Proof of Concept
1. Owner deploys `WrappedHyperFungibleToken`, calls `configure()` with `_underlying` set to a fee-on-transfer ERC20 (e.g., 1% fee, non-native path, `_isWeth = false`).
2. Alice calls `send({dest, to: bob, amount: 1000, timeout: T, relayerFee: 0, data: ""})`.
   - `safeTransferFrom(alice, address(this), 1000)` actually delivers only `990` to the contract (fee-on-transfer).
   - The dispatched `Message.amount` is `1000` (unadjusted), and the `Sent` event reports `amount: 1000`.
3. Suppose the ISMP request times out before delivery (e.g., relayer never submits it, or destination `onAccept` rejects it and it later times out per ISMP timeout semantics).
4. `onPostRequestTimeout` is invoked with the same `message.amount = 1000` and calls `IERC20(_underlying).safeTransfer(alice, 1000)`.
5. The contract holds only `990` of the underlying (assuming no other deposits inflate the balance), so the `safeTransfer` reverts — Alice's `990` tokens are stuck, and the timeout can never be finalized for this request, permanently freezing funds and blocking the ISMP timeout callback from ever succeeding for that commitment.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L234-253)
```text
    function _buildDispatchPost(HyperFungibleToken.SendParams calldata params) internal view returns (DispatchPost memory) {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(HyperFungibleToken.Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));

        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-290)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-336)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L344-365)
```text
    function onPostRequestTimeout(PostRequestTimeout calldata incoming) external override onlyHost whenNotPaused {
        HyperFungibleToken.Message memory message = abi.decode(incoming.request.body, (HyperFungibleToken.Message));
        address refundee = _toAddr(message.from);

        if (_isWeth) {
            // Try a native-ETH push first; if the refundee cannot accept native value
            // (e.g. the caller used the ERC-20 deposit path in `send()` from a
            // non-payable contract), re-wrap the withdrawn ETH and deliver the
            // underlying WETH as an ERC-20 transfer so the timeout still settles and
            // funds are not permanently locked.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = refundee.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(refundee, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(refundee, message.amount);
        }

        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L312-323)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```
