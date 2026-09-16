### Title
`onPostRequestTimeout` refund path is gated by `whenNotPaused`, permanently locking burned tokens with no fallback recovery - ([File: sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol])

### Summary
`HyperFungibleTokenUpgradeable.send()` burns the caller's tokens before dispatching a cross-chain ISMP POST request. The only way those tokens are ever restored is `onPostRequestTimeout`, which re-mints them to the original sender if the message never gets delivered. That refund function carries the `whenNotPaused` modifier, so if the token is paused at any point between the burn and the timeout being processed, the refund reverts and the user's burned funds cannot be recovered until (and unless) the owner unpauses the contract.

### Finding Description
`send()` unconditionally burns the caller's balance and dispatches the request: [1](#0-0) 

The only remediation path for a request that never gets delivered (times out) is: [2](#0-1) 

This function is gated with `whenNotPaused`, and `pause()`/`unpause()` are exclusively owner-controlled: [3](#0-2) 

The project's own design-decision notes confirm this gating is deliberate ("Timeouts mint a refund to the original sender, so a forged timeout proof mints"), contrasted against the intent gateway, which does not gate its timeout callback at all. This is structurally identical to the external report's bug class: a boolean/administrative state flag (`allow_extensions` in the kiosk analog, `paused` here) gates the one function (`uid_mut` there, `onPostRequestTimeout` here) needed to reach or recover funds that were already committed into the protocol (locked in an extension vs. burned pending an ISMP round-trip), and there is no fallback mechanism to unblock recovery of funds that were already in flight when the flag was flipped.

The same pattern is repeated in the sibling lock-and-release contract, `WrappedHyperFungibleTokenUpgradeable`, whose `send()` is also `whenNotPaused` and whose refund/timeout handling follows the same token base: [4](#0-3) 

### Impact Explanation
An unprivileged user who calls `send()` has their tokens burned (or, for the wrapped variant, escrowed) atomically with the dispatch. If the token owner pauses the contract at any time before the message is delivered or before its timeout is processed — for routine operational reasons, an incident response, or simply because the message happens to be slow relative to a scheduled pause — the relayer's `handlePostRequestTimeouts` call into `onPostRequestTimeout` will revert. Per the handler's documented behaviour, timeouts can be resubmitted, but only once the contract is unpaused; there is no alternate code path that lets the user or anyone else reclaim the burned balance while paused. If the pause is never lifted (owner key loss, abandoned deployment, or an intentional freeze), the burned funds are permanently unrecoverable — a direct freezing-of-funds outcome triggered by a normal token operation (`send`) plus a normal owner action (`pause`), not by any malicious or governance-compromise scenario.

### Likelihood Explanation
Every `send()` call from any user creates a window during which their tokens are burned but not yet confirmed delivered or refunded. `pause()` is a single, unprivileged-reachable-effect action (callable at will by the owner for benign operational reasons, e.g. responding to a discovered issue elsewhere in the system) that can land inside this window for any in-flight message. Given that timeouts are the expected, routine failure mode of cross-chain messaging (network delay, no relayer picking up the message, destination congestion), the race between an ordinary pause and an in-flight timeout is not a contrived edge case.

### Recommendation
Remove the `whenNotPaused` modifier from `onPostRequestTimeout` (and from any other purely fund-recovery/refund callback), or introduce an explicit unpausable-refund fallback so that funds already committed prior to a pause can always be recovered, mirroring the remediation the external report describes (removing the blocking gate rather than leaving committed funds hostage to an administrative flag with no escape hatch). If the pause is retained for `onPostRequestTimeout` to prevent a forged-timeout mint under a compromised consensus client, gate it on a narrower "consensus is untrusted" condition rather than the general operational pause switch, so a routine pause cannot strand funds indefinitely.

### Proof of Concept
1. Attacker/user calls `send()` with `params.amount = X`, burning `X` tokens and dispatching a POST request with a nonzero `timeout`. [1](#0-0) 
2. Before the message is delivered, the owner calls `pause()` (for any reason unrelated to this user's transfer). [5](#0-4) 
3. The request times out on the source host; a relayer calls `HandlerV2.handlePostRequestTimeouts`, which invokes `onPostRequestTimeout` on the token.
4. The call reverts due to `whenNotPaused`, and per protocol docs the timeout must be resubmitted later — but only after `unpause()` is called, which the user cannot trigger themselves. [2](#0-1) 
5. Until the owner unpauses (which may never happen), the user's `X` tokens are burned with no minted balance anywhere — funds are frozen/lost.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L245-255)
```text
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L344-349)
```text
    function onPostRequestTimeout(PostRequestTimeout memory incoming) external override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L294-318)
```text
    function send(HyperFungibleTokenUpgradeable.SendParams calldata params) external payable whenNotPaused {
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
