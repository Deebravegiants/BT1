## Analog Found

### Title
Permanent freeze of escrowed/bridged funds via push-only ERC20 transfers with no pull-based recovery - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
The Moloch report flags a design where the DAO *pushes* tribute tokens back to the proposer, and if that push is ever blocked (blacklisted/paused token), the funds get stuck with no fallback pull mechanism. Hyperbridge's Intent Gateway (`ExtrinsicIntents.sol` / `IntentsBase.sol`) and the `HyperFungibleToken`/`WrappedHyperFungibleToken` bridge apps have the exact same structural weakness: settlement, cancellation, refund and timeout paths all resolve to a single unconditional push (`safeTransfer`/`transfer`) to a fixed beneficiary address baked into the order/message, with no pull-based fallback if that specific transfer permanently reverts.

### Finding Description
`IntentsBase._withdraw` is the single code path used by fills (`RedeemEscrow`), cross-chain cancellations (`RefundEscrow`), and the GET-response cancel-from-source flow. It unconditionally calls `IERC20(token).safeTransfer(beneficiary, amount)`: [1](#0-0) 

The `beneficiary` is fixed at order-placement time (`order.user`) or is whichever address filled the order (the solver), and cannot be redirected later: [2](#0-1) 

This `_withdraw` is invoked from `onAccept` (settlement/refund) and `onGetResponse` (cancel-from-source): [3](#0-2) [4](#0-3) 

`EvmHost.dispatchIncoming` catches the revert and marks the message retryable rather than failing the whole batch: [5](#0-4) 

This retry mechanism only helps for *transient* failures. If the token used for `inputs`/escrow is a blacklist-capable/pausable token (USDC, USDT — both used as canonical examples throughout the test suite, e.g. `usdc.approve(...)` in `evm/tests/foundry/IntentGatewayV2Test.sol`) and the fixed beneficiary (the user on refund/cancel, or the solver on fill) is or becomes blacklisted, `safeTransfer` will revert **every single time** the message is resubmitted — indefinitely. Since the beneficiary address is derived from immutable order data and there is no admin/governance override or pull-based claim function for escrowed order funds (only `SweepDust`, which only touches accumulated protocol fee dust, not user escrow), the tokens become permanently frozen in the gateway contract with no recovery path — precisely the failure mode the Moloch report describes.

The same push-only pattern, with the same lack of a pull fallback, exists in the token-bridge apps used for cross-chain transfers and timeout refunds: [6](#0-5) [7](#0-6) 

If the recipient (`onAccept`) or the original sender (`onPostRequestTimeout`) is blacklisted by the underlying token, delivery/refund can never succeed, and the locked/escrowed underlying tokens are frozen forever.

### Impact Explanation
Escrowed order inputs (Intent Gateway) or bridge-locked/burned tokens (HyperFungibleToken/WrappedHyperFungibleToken) can become permanently unrecoverable whenever the fixed beneficiary address is blacklisted by the ERC20 token in use, or the token pauses transfers to that address for any reason. This is a genuine permanent freezing of user/solver funds reachable via ordinary user-facing flows (`placeOrder`/`fillOrder`/`cancelOrder`/`send`) — no privileged actor required.

### Likelihood Explanation
Moderate-to-high: many major stablecoins used as bridge/escrow assets (USDC, USDT) support blacklisting, and the test suite itself demonstrates USDC/DAI as typical order tokens. A user or solver whose address is later sanctioned/blacklisted (or one that deliberately places/fills orders using a token+address combination they know will be blocked) will permanently trap the corresponding escrow with no available remediation in the contract.

### Recommendation
Replace the unconditional push-transfer pattern in `_withdraw` (`IntentsBase.sol`), `withdraw` (`IntentGatewayV2.sol`), and the bridge apps' `onAccept`/`onPostRequestTimeout` with a pull-based claim pattern: on transfer failure, credit an internal balance mapping for the beneficiary and let them (or anyone, permissionlessly, to any address they control) call a separate `withdraw(token)` function to claim the funds later, rather than reverting the whole settlement/refund/timeout call indefinitely.

### Proof of Concept
1. User places a cross-chain order with `inputs` denominated in USDC, `order.user = attacker/blacklist-candidate address`.
2. Before the order is filled, the `order.user` address (or, in the fill case, the solver's address) is added to USDC's blacklist (a realistic external event, or self-inflicted by using an address the user controls that a stablecoin issuer later sanctions).
3. Order expires; `cancelOrder` is invoked from the destination chain, dispatching `RefundEscrow` back to the source chain.
4. On the source chain, `onAccept` → `_withdraw` calls `IERC20(usdc).safeTransfer(blacklistedUser, amount)`, which reverts every time due to USDC's blacklist check.
5. `EvmHost.dispatchIncoming` marks the message retryable, but resubmission never succeeds since the underlying condition (blacklist) does not change.
6. The escrowed USDC remains permanently locked in the `IntentGateway`/`ExtrinsicIntents` contract with no pull-based mechanism to recover it.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-366)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-326)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

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

    /**
     * @notice Handles timeout of a previously dispatched cross-chain transfer
     * @dev Called by the ISMP host when a sent message times out without being delivered.
     * Re-mints the burned tokens back to the original sender as a refund.
     * @param incoming The timed-out POST request and the relayer that submitted the timeout proof
     */
    function onPostRequestTimeout(PostRequestTimeout memory incoming) public virtual override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L300-336)
```text
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
