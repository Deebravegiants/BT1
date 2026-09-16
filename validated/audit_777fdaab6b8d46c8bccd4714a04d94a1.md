### Title
Paused HyperFungibleToken blocks `onPostRequestTimeout` refunds, permanently stranding already-burned user funds - (File: `sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol`)

### Summary
`HyperFungibleTokenUpgradeable` (and its `WrappedHyperFungibleTokenUpgradeable` counterpart) gates `send`, `onAccept`, **and** `onPostRequestTimeout` behind the same `whenNotPaused` modifier. Because `send()` burns the caller's tokens before dispatching the cross-chain POST request, a subsequent timeout is the *only* path that returns those tokens to the sender. If the contract is paused after a transfer has already been dispatched but before the message times out, the refund path is blocked exactly like the vault's `withdrawalRequest` in the referenced M-10 report, leaving users' already-burned funds unrecoverable until an owner action restores availability.

### Finding Description
`send()` immediately burns the sender's balance and dispatches an ISMP POST request: [1](#0-0) 

If the destination never accepts the request (e.g. congestion, relayer unavailability, or destination chain issues), the host eventually calls `onPostRequestTimeout`, which is supposed to re-mint the burned tokens back to the original sender: [2](#0-1) 

However, this refund entrypoint carries the same `whenNotPaused` guard as the outbound `send()` and inbound `onAccept()` functions: [3](#0-2) 

This mirrors the structural flaw in the M-10 report: a state transition (there, "inactive vault"; here, "paused contract") is meant to halt *new* activity (deposits/`send`, mints/`onAccept`), but it also disables the recovery/refund mechanism for **already-in-flight** operations that were initiated before the state change. Just as the derby vault held no funds to satisfy an immediate withdrawal but should still have accepted a `withdrawalRequest` for future processing, here the tokens are already burned (there is nothing left to "protect" by pausing this call) — pausing the refund path serves no protective purpose but strands user funds that were already committed to the bridge.

### Impact Explanation
Any user whose `send()` transaction is in flight when the token is paused, and whose destination-side delivery subsequently fails or is delayed past the timeout, cannot reclaim their burned tokens for as long as the pause remains active. Since pause has no expiry and depends entirely on a future `unpause()` call, this is a freezing-of-funds condition: user balances are burned with no way back until an external action restores the function, which the user cannot control or force. This satisfies "permanent freezing of funds" for the class of in-flight transfers caught in this window, matching the accepted Medium severity of the analog issue.

### Likelihood Explanation
Pausing is a standard operational safety switch expected to be exercised during incidents (the very scenarios where relays are more likely to stall and timeouts are more likely to occur), so overlap between an active pause and outstanding timeouts is a realistic and plausible occurrence rather than a contrived edge case. No malicious actor is required — a routine incident-response pause is sufficient to trigger the freeze for users who transacted just before it.

### Recommendation
Do not gate `onPostRequestTimeout` (and `onAccept`, to the extent it represents already-dispatched funds arriving) behind `whenNotPaused`. Pausing should stop new state-changing user-initiated flows (`send`, `transfer`, `transferFrom`) but must still allow completion/refund of operations that were already committed, mirroring the fix recommended for the derby vault: allow the "recovery" leg of an operation to proceed independent of the paused/inactive gate.

### Proof of Concept
1. User calls `send()` with `amount = X`; `X` tokens are burned and a POST request with a timeout is dispatched. [1](#0-0) 
2. Before the destination chain accepts the message, the owner calls `pause()` (e.g., in response to an unrelated incident). [4](#0-3) 
3. The destination request times out; a relayer submits the timeout proof to the host, which calls `onPostRequestTimeout` on this contract.
4. The call reverts due to `whenNotPaused`, so the user's `X` tokens are never re-minted. [5](#0-4) 
5. The user's `X` tokens remain unrecoverable until the owner calls `unpause()`, and if the timeout proof submission window/relayer incentive has passed, may become effectively unrecoverable.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L241-255)
```text
    /**
     * @notice Pauses all cross-chain operations (send and receive)
     * @dev Only callable by the contract owner
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @notice Unpauses all cross-chain operations
     * @dev Only callable by the contract owner
     */
    function unpause() external onlyOwner {
        _unpause();
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L293-311)
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L338-349)
```text
    /**
     * @notice Handles timeout of a previously dispatched cross-chain transfer
     * @dev Called by the ISMP host when a sent message times out without being delivered.
     * Re-mints the burned tokens back to the original sender as a refund.
     * @param incoming The timed-out POST request and the relayer that submitted the timeout proof
     */
    function onPostRequestTimeout(PostRequestTimeout memory incoming) external override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```
