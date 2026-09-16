## Title
Underlying tokens with an external blacklist (e.g. USDC) can become permanently frozen in `WrappedHyperFungibleToken` with no recovery path for either delivery or timeout refund - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken` wraps an arbitrary underlying ERC20 (explicitly designed to support tokens like USDC/USDT that implement compliance blacklists). Both the delivery path (`onAccept`) and the timeout-refund path (`onPostRequestTimeout`) push the underlying token directly to a fixed address extracted from the cross-chain message body, with no fallback, retry, or admin-sweep mechanism if that transfer reverts. If the destination beneficiary or the original sender becomes blacklisted by the underlying token's issuer after the message is dispatched but before it is delivered or times out, the locked tokens become permanently unrecoverable — mirroring the reported OpenQ pattern where a blacklisted asset can neither be delivered as originally intended nor refunded.

### Finding Description
`send()` locks the underlying ERC20 from `msg.sender` and dispatches an ISMP POST request whose body encodes the beneficiary (`to`) and the original sender (`from`), used later for delivery or refund respectively: [1](#0-0) 

On delivery, `onAccept` decodes the beneficiary and unconditionally calls `safeTransfer` to it: [2](#0-1) 

On timeout, `onPostRequestTimeout` decodes the original sender and unconditionally calls `safeTransfer` to refund them: [3](#0-2) 

Neither path offers any way to redirect the transfer to a different address, retry with a different recipient, or sweep the locked funds to a designated account if `safeTransfer` (or the WETH unwrap/re-wrap fallback) reverts. For blacklist-capable tokens such as USDC, a `safeTransfer` to a blacklisted address reverts unconditionally and permanently (until the issuer, an entity outside this protocol's control, removes the address from its blacklist — which the protocol cannot compel or predict). Because `onAccept` is the only path to deliver the locked funds and `onPostRequestTimeout` is the only path to refund them, and both target the same fixed, message-embedded address, a blacklisting event occurring after dispatch permanently blocks whichever of the two paths is later attempted. There is no `isWhitelisted`/`isBlacklisted` pre-check, no configurable beneficiary override, and no admin rescue function anywhere in this contract for funds tied to a specific in-flight commitment.

### Impact Explanation
Any unprivileged user can call `send()` targeting an arbitrary beneficiary address on any configured destination chain. If the underlying token's issuer blacklists either the sender or the beneficiary address after the message is in flight (a realistic, external, and unprivileged-triggerable event for real-world stablecoins), the locked underlying tokens are permanently frozen in the contract: delivery reverts forever via `onAccept`, and if the message instead times out, the refund also reverts forever via `onPostRequestTimeout`. This is a permanent freezing of user funds with no code path for recovery, satisfying the "permanent freezing of funds" impact bar.

### Likelihood Explanation
The precondition (issuer-side blacklisting) is outside the depositor's control but is a well-known and common real-world event for the exact class of stablecoins (USDC/USDT) this wrapper is built to support (`isWeth`/generic ERC20 wrapping is explicitly designed in, and the natural high-value underlying assets are blacklist-capable stablecoins). Triggering it does not require any privileged action within Hyperbridge — an ordinary user can simply send funds to (or from) an address that is later sanctioned/blacklisted, or an attacker could deliberately target an address they know will be blacklisted to grief that specific transfer permanently. This makes the bug practically reachable from a single unprivileged `send()` call.

### Recommendation
Add a recovery mechanism decoupled from the fixed beneficiary/refundee address:
- If `safeTransfer` fails in `onAccept` or `onPostRequestTimeout`, fall back to crediting an internal, pull-based balance mapping (escrow accounting) instead of reverting the entire message processing, similar to patterns used for WETH-push fallback already present in this file.
- Alternatively, allow the contract owner (or the original committed beneficiary via a signed message) to redirect stuck funds to an alternate address after a grace period, analogous to the recommendation in the referenced report of allowing refund/redirection independent of the original recipient once a token becomes unusable.
- Ensure `onAccept`/`onPostRequestTimeout` cannot be permanently blocked by a single unresolvable external transfer, since this also blocks all other batched processing dependent on host state.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` wrapping USDC as `_underlying`.
2. User A calls `send()` with `to` = address B, locking USDC in the contract and dispatching an ISMP POST request.
3. Before the message is relayed/delivered, USDC issuer blacklists address B (a real, external, unprivileged-to-Hyperbridge event).
4. Relayer submits the proof; `onAccept` is invoked, decodes beneficiary = B, and calls `IERC20(_underlying).safeTransfer(B, amount)` — this reverts unconditionally per USDC's blacklist enforcement, so delivery can never succeed.
5. If instead the message times out (e.g., relayer never delivers in time), `onPostRequestTimeout` is invoked with `from` = A. If A is blacklisted instead of B, the refund `safeTransfer(A, amount)` reverts unconditionally as well.
6. In either case, the locked USDC remains in the contract indefinitely with no function available to redirect or sweep it to a usable address.

### Citations

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
