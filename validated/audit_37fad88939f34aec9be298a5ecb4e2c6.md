### Title
`fundRequest()` lets anyone top up a relayer fee, but the entire accumulated fee — including third-party top-ups — is refunded only to the original `payer` recorded at dispatch time - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.fundRequest()` is a permissionless function that lets any caller add fee-token funds to an already-dispatched request's relayer fee. However, the added funds are merged into the request's single `FeeMetadata.fee` and, on timeout, the *entire* amount is refunded to `FeeMetadata.sender` — the `payer` address that was recorded when the request was originally dispatched, not the address that called `fundRequest`. This mirrors the reported analog: a function that moves value based on an "account"/"payer" field which is not guaranteed to correspond to whoever actually supplied the funds in a given call, with no access control tying the two together.

### Finding Description
`EvmHost.dispatch(DispatchPost)` lets the caller supply an arbitrary `payer` address, stored verbatim as the refund beneficiary: [1](#0-0) 

`fundRequest()` is permissionless (`external payable`, no access-control modifier beyond `notFrozen`) and increases `metadata.fee` for an existing commitment using funds pulled from `_msgSender()` (whoever calls it), but it never updates or records the identity of this new funder — it only reuses the original `metadata.sender`: [2](#0-1) 

When the request eventually times out, the *entire* `metadata.fee` (original fee + any top-ups from `fundRequest`) is refunded solely to `metadata.sender`: [3](#0-2) [4](#0-3) 

This is structurally identical to the reported bug class: a function callable by anyone that moves assets to/from an "account"/"payer" parameter that is not verified to be the entity that actually funded the current call, and which the attacker fully controls at request-creation time.

### Impact Explanation
A malicious dispatcher can create a POST/GET request with `payer = attacker`, a near-zero relayer fee, and a destination/body engineered to guarantee delivery failure or non-relaying (e.g., an unroutable `to` module, or a destination chain/app that will always revert `onAccept`, ensuring the request times out rather than being delivered). If any third party (an automated relayer top-up service, another dApp, or an unrelated user trying to speed up delivery) calls `fundRequest()` on this commitment to add real fee-token funds, those funds become indistinguishable from the original fee. When the request times out, the attacker (as `payer`) reclaims the *entire* fee, including the third party's contribution — a direct, unbacked transfer of value from the funder to the attacker with no compensating action. This is a concrete theft of funds reachable by a single permissionless call (`fundRequest`) against an attacker-crafted, already-dispatched request.

### Likelihood Explanation
`fundRequest` is explicitly designed to be callable by anyone ("Additional fee refunded to `payer` if request times out" — permissionless, per the protocol docs), and relayer/incentive infrastructure around Hyperbridge is expected to proactively top up under-funded pending requests to encourage delivery. This makes it plausible that automated funder services or well-meaning users will call `fundRequest` on attacker-created, deliberately-doomed requests, at which point the mismatch between funder and refund-beneficiary directly benefits the attacker.

### Recommendation
Track fee contributions per-funder (e.g., a mapping from commitment → funder → amount) and refund each funder their own contribution on timeout, rather than collapsing all top-ups into a single `FeeMetadata.fee`/`sender` pair. Alternatively, require `fundRequest` callers to specify their own refund address and only allow the original request's fee (not later top-ups) to go to `payer`, so no unrelated party's fee-token contribution can be captured by the original dispatcher.

### Proof of Concept
1. Attacker calls `EvmHost.dispatch(DispatchPost{ ..., fee: 0, payer: attacker, to: <address of a module guaranteed to revert or be unroutable>, timeout: T })`, obtaining `commitment`. [1](#0-0) 
2. A third-party funder (e.g., automated fee-bumping bot) observes the low-fee pending request and calls `EvmHost.fundRequest(commitment, amount)`, transferring `amount` of fee tokens from itself into the contract; this is merged into `_requestCommitments[commitment].fee` without recording the funder's address. [2](#0-1) 
3. Because delivery to the crafted `to`/module reverts or is never attempted, the request times out at `T`.
4. Anyone submits the timeout proof; `dispatchTimeOut`/`GetRequestTimeout` handling refunds `metadata.fee` (original fee + funder's `amount`) entirely to `metadata.sender == attacker`. [3](#0-2) 
5. The attacker has now received `amount` of the funder's tokens with no reciprocal action, while the funder receives nothing back.

### Citations

**File:** evm/src/core/EvmHost.sol (L871-877)
```text

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/EvmHost.sol (L898-906)
```text
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/EvmHost.sol (L921-948)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }

        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
```

**File:** evm/src/core/EvmHost.sol (L1031-1051)
```text
    function fundRequest(bytes32 commitment, uint256 amount) external payable notFrozen {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                amount, path, address(this), block.timestamp
            );
        } else {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), amount);
        }

        FeeMetadata memory metadata = _requestCommitments[commitment];
        if (metadata.sender == address(0)) revert UnknownRequest();

        metadata.fee += amount;
        _requestCommitments[commitment] = metadata;

        emit RequestFunded({commitment: commitment, newFee: metadata.fee});
    }
```
