## Title
Fee amounts recorded before a `feeToken` rotation are paid out against the *new* fee token, draining funds contributed by new fee payers - (File: `evm/src/core/EvmHost.sol`)

## Summary
This is the Hyperbridge analog of the `PaladinRewardReserve.approvedSpenders` bug: a data structure records a *value* without recording which *token* that value is denominated in, and the surrounding functions later act on that value using whatever token is "currently" configured rather than the token that was originally associated with it. In `EvmHost.sol`, `FeeMetadata` (stored per request in `_requestCommitments`) only stores `{ sender, fee }` — a raw `uint256` amount — with no token identifier [1](#0-0) . Every payout of that `fee` (relayer reward on delivery, refund on timeout, top-up via `fundRequest`) always uses `feeToken()`, i.e. whatever token is *currently* configured in `_hostParams.feeToken` [2](#0-1) [3](#0-2) [4](#0-3) .

## Finding Description
`updateHostParamsInternal` allows governance to rotate `feeToken` to a new address, and the only safety check is that the *old* token's balance on the host is zero at the moment of rotation:

```solidity
address oldFeeToken = feeToken();
if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
    uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
    if (balance != 0) revert CannotChangeFeeToken();
}
``` [5](#0-4) 

This check only guards against the host still literally holding old-token balance; it says nothing about outstanding `_requestCommitments` entries whose `fee` was denominated (and paid for) in the old token. Because `withdraw` lets governance sweep the old token's balance to the treasury/beneficiary at any time [6](#0-5) , an ordinary, legitimate operational sequence — sweep old-token revenue, then rotate `feeToken` (exactly the kind of "governance can update [feeToken] without a redeploy" flow the docs describe) [7](#0-6)  — leaves the old-token balance at zero while `_requestCommitments` still contains live entries whose `fee` was collected and is owed in the *old* token.

Once the rotation completes, every one of `EvmHost`'s permissionless/relayer-facing entry points reads `fee` from the stale commitment but pays it in the *new* `feeToken()`:

- `dispatchIncoming(PostRequest, relayer)` — pays the relayer `IERC20(feeToken()).safeTransfer(relayer, fee)` using the old numeric `fee` against the new token [8](#0-7) .
- `dispatchIncoming(GetResponse, relayer)` — same pattern [2](#0-1) .
- `dispatchTimeOut(GetRequestTimeout, meta, commitment)` and `dispatchTimeOut(PostRequestTimeout, meta, commitment)` — refund `meta.sender` the stale `fee` amount out of `feeToken()` [9](#0-8) .
- `fundRequest(commitment, amount)` — adds `amount` (paid in the *new* `feeToken()`) onto a `metadata.fee` that was originally denominated in the *old* token, silently mixing units in the same accumulator [4](#0-3) .

None of these functions verify which token the stored `fee` was actually paid in — exactly the missing-token-identity defect the Paladin report describes for `approvedSpenders`. The host's `feeToken()` balance is a shared pool funded by *all* fee payers dispatching after the rotation; paying out stale, old-token-denominated `fee` values from that pool means new fee payers' funds are used to satisfy claims they never funded, at whatever numeric value happens to have been recorded under the old token's (possibly different) decimals/valuation.

## Impact Explanation
This directly drains value from the new fee-token pool to pay stale relayer rewards/refunds that were never funded in that token, and it does so through fully permissionless entry points (`dispatchIncoming`, `dispatchTimeOut`, `fundRequest` are called by relayers/handlers/anyone, not governance). Because the numeric `fee` was priced for the old token's decimals/economics, a rotation to a token with different decimals or value can cause gross over/under payment. In the worst case this is concrete theft/misallocation of funds contributed by unrelated, honest fee payers on the new token — a High-severity fund-safety issue reachable without any malicious governance action, only a routine (and documented-as-supported) fee-token rotation combined with ordinary relayer/user activity.

## Likelihood Explanation
`feeToken` rotation is an explicitly supported, non-malicious governance capability (the docs describe it as something "governance can update... without a redeploy") [7](#0-6) , and sweeping accrued revenue via `withdraw` before a rotation is the natural operational order. Any request dispatched with a nonzero fee before the rotation and delivered/timed-out/topped-up after it will trigger the mismatch — this requires no attacker collusion with governance, just normal message traffic straddling a token rotation.

## Recommendation
Store the token identity alongside each `FeeMetadata` entry (e.g. `struct FeeMetadata { address sender; address token; uint256 fee; }`), and have `dispatchIncoming`, both `dispatchTimeOut` overloads, and `fundRequest` transfer/refund using the token recorded in the commitment rather than the live `feeToken()`. Alternatively, block `updateHostParams` from changing `feeToken` while any `_requestCommitments`/pending GET entries with nonzero `fee` still exist (not just while the host's balance is nonzero), ensuring all outstanding fee obligations are settled in their original token before rotation.

## Proof of Concept
1. User A dispatches a `PostRequest` via `dispatch(DispatchPost)` with `fee = 100` paid in `feeToken` = TokenX; this creates `_requestCommitments[c] = {sender: A, fee: 100}` [10](#0-9) .
2. Governance withdraws the host's entire TokenX balance to the treasury via `withdraw` [11](#0-10) , then calls `updateHostParams` to rotate `feeToken` to TokenY; the `CannotChangeFeeToken` check passes because TokenX balance is now zero [5](#0-4) , even though commitment `c` (100 TokenX) is still outstanding.
3. Other users dispatch new requests, paying fees in TokenY, building up a TokenY balance on the host.
4. A relayer delivers request `c`'s handler execution (via `dispatchIncoming`); the host reads `_requestCommitments[c].fee = 100` and pays the relayer `100` units of `feeToken()` — now TokenY — out of the pool funded by the other users' TokenY fees, even though nobody ever paid 100 TokenY for request `c` [8](#0-7) .

### Citations

**File:** evm/src/core/EvmHost.sol (L617-621)
```text
        address oldFeeToken = feeToken();
        if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
            uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
            if (balance != 0) revert CannotChangeFeeToken();
        }
```

**File:** evm/src/core/EvmHost.sol (L647-660)
```text
    /**
     * @dev withdraws host revenue to the given address, can only be called by cross-chain governance
     * @param params, the parameters for withdrawal
     */
    function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
        if (params.token == address(0)) {
            // this is safe because re-entrancy is mitigated before dispatching requests
            (bool sent,) = params.beneficiary.call{value: params.amount}("");
            if (!sent) revert WithdrawalFailed();
        } else {
            IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
        }
        emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
    }
```

**File:** evm/src/core/EvmHost.sol (L811-818)
```text

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L841-847)
```text
        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L856-906)
```text
    function dispatchTimeOut(
        GetRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onGetTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }

    /**
     * @dev Dispatch an incoming POST timeout to the source module
     * @param timeout - timed-out post request bundled with the relayer that submitted the timeout proof
     * @param meta - fee metadata for the original request
     * @param commitment - request commitment
     */
    function dispatchTimeOut(
        PostRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onPostRequestTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/EvmHost.sol (L908-948)
```text
    /**
     * @dev Dispatch a POST request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the feeToken.
     *
     * @param post - post request
     * @return commitment - the request commitment
     */
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
