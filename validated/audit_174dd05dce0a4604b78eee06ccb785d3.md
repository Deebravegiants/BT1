### Title
Unbacked Cross-Chain Claims from Rebasing/Fee-on-Transfer Underlying Tokens in `WrappedHyperFungibleToken` - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken` locks an underlying ERC20 on the home chain and lets peer chains mint/unlock the exact nominal `amount` encoded in the cross-chain message, without ever checking how many underlying tokens the contract actually received or actually holds. If the configured `_underlying` is a rebasing token (e.g. stETH-style) or a fee-on-transfer/deflationary token — the same token class the referenced report is about — the contract's real balance diverges from the sum of `amount` values it has promised to peer chains, producing insolvency and stuck/undeliverable withdrawals.

### Finding Description
`send()` locks tokens using `safeTransferFrom(msg.sender, address(this), params.amount)` and then dispatches a message whose body carries `params.amount` as the nominal locked value: [1](#0-0) 

`_buildDispatchPost` encodes exactly `params.amount` into the `Message.amount` field that is trusted verbatim by the recipient side: [2](#0-1) 

There is no post-transfer balance check (`balanceOf(this)` before/after) anywhere in `send()`, and `onAccept()`/`onPostRequestTimeout()` unconditionally `safeTransfer(beneficiary, message.amount)` the nominal amount, again with no reconciliation against the contract's actual underlying balance: [3](#0-2) [4](#0-3) 

This is the same root cause described in the external report: the code assumes 1:1 correspondence between a nominal token accounting unit and the actual token balance held in custody, and does not account for token mechanics (rebasing, transfer fees) that break that assumption. If:
- the underlying is fee-on-transfer/deflationary, `safeTransferFrom` delivers less than `params.amount` into the contract, but the message still promises the full `params.amount` to the destination chain, or
- the underlying is a rebasing token that can rebase downward (negative rebase), the contract's held balance can fall below the sum of `amount`s already dispatched to peers,

then the contract becomes under-collateralized relative to its cross-chain liabilities. The `WrappedHyperFungibleTokenUpgradeable` variant has the identical pattern.

### Impact Explanation
Once the wrapper's actual underlying balance falls below the total of `amount`s it owes across all outstanding/incoming messages:
- Legitimate `onAccept` deliveries for later users will revert (`safeTransfer` reverting on insufficient balance), permanently stalling — and depending on relayer/timeout handling, permanently freezing — those users' funds since the route can no longer deliver the message it committed to.
- Earlier users effectively drain the pool faster than they deposited real value, at the expense of users whose messages settle later — a fund-theft/insolvency pattern rather than mere idle-yield accumulation as in the original report (this contract's design makes the direction of the mismatch a solvency risk, not merely un-swept surplus like the EToken excess-collateral case).

This satisfies "concrete theft or permanent freezing of funds ... or a route unable to deliver messages" from an unprivileged, single-transaction path (`send()`).

### Likelihood Explanation
The trigger requires the deployment's `_underlying` to be a fee-on-transfer or rebasing token — a configuration made once via `configure()`/`WrappedConfigOptions.underlying`, analogous to how the referenced EToken/Liquity fork legitimately configures stETH as collateral. Given that both fee-on-transfer tokens (e.g., USDT under fee mode) and rebasing tokens (e.g., stETH) are real, commonly bridged asset classes, and nothing in the contract or its documented API restricts `underlying` to "standard" ERC20s, any wrapper deployment using such a token is directly and repeatedly exploitable by ordinary `send()` calls from any user — no privileged or malicious-admin action is required to trigger the accounting break itself.

### Recommendation
Measure the actual underlying balance delta around `safeTransferFrom` in `send()` and use that measured amount (not `params.amount`) in the dispatched `Message.amount`. On the receiving side, before `safeTransfer`, verify the wrapper's actual `underlying` balance covers `message.amount`, and either revert distinctly or account for shortfalls explicitly rather than assuming balance and nominal accounting units are always equal. If rebasing/fee-on-transfer tokens are to be supported at all, implement share-based accounting (as recommended in the source report) so custody amounts track real balances rather than nominal transfer amounts.

### Proof of Concept
1. Owner deploys `WrappedHyperFungibleToken` and configures it with `underlying` set to a fee-on-transfer token (e.g., a token that takes a 2% fee on `transfer`/`transferFrom`).
2. Alice calls `send({amount: 1000, ...})`. `safeTransferFrom` pulls 1000 nominal but only 980 actually lands in the contract (`balanceOf(this)` increases by 980). The dispatched `Message.amount` is still `1000`. [5](#0-4) 
3. On the destination chain's peer `WrappedHyperFungibleToken`, `onAccept` releases the full `message.amount` (1000) worth of the peer's own escrowed underlying to the beneficiary — over-releasing relative to what was actually locked on the source side. [6](#0-5) 
4. Repeating this drains the destination-side custody faster than the source-side lock backs it; eventually a legitimate `onAccept` for another user reverts because the destination contract's real `underlying` balance is insufficient to pay out the nominal `message.amount`, freezing that user's incoming transfer.

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
