Confirmed vulnerability. The `send()` function locks tokens via `safeTransferFrom` without measuring actual received balance, then dispatches the full nominal `params.amount` in the message body, and `onAccept`/`onPostRequestTimeout` both unlock the full `message.amount` regardless of what was actually received on lock.

### Title
Fee-on-transfer tokens cause reserve shortfall and cross-user fund freezing in `WrappedHyperFungibleToken.send()` - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.send()` locks the underlying ERC20 via `safeTransferFrom(msg.sender, address(this), params.amount)` and then commits/dispatches a cross-chain message asserting that `params.amount` was locked, without ever checking the contract's actual token balance delta. If the underlying token charges a transfer fee (fee-on-transfer / deflationary token), the contract receives strictly less than `params.amount`, yet the ISMP message still claims the full nominal amount was locked.

### Finding Description
In `send()`: [1](#0-0) 
the contract calls `IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount)` and immediately builds/dispatches a `DispatchPost` whose body encodes `HyperFungibleToken.Message{ ..., amount: params.amount, ... }` via `_buildDispatchPost` at [2](#0-1) 
There is no balance-before/balance-after check to determine the actual amount received (unlike the fee-on-transfer handling already implemented in `IntentGatewayV2.placeOrder`, which explicitly measures `balBefore`/`balanceOf` deltas, see `evm/src/apps/IntentGatewayV2.sol#L313-L328` and its dedicated `FeeOnTransferToken` tests). On the destination side, `onAccept` unlocks/transfers `message.amount` (the full nominal amount) to the beneficiary: [3](#0-2) 
and `onPostRequestTimeout` also refunds the full nominal `message.amount` back to the original sender: [4](#0-3) 

This means every `send()` call with a fee-on-transfer underlying token leaves the contract permanently under-collateralized by the fee amount relative to what it has promised to release (either via delivery on the destination chain's mirrored contract, or via timeout refund on this chain). Since the underlying balance is a shared pool across all users of that token pair, this shortfall accumulates and eventually causes `onAccept`/`onPostRequestTimeout` calls for other unrelated users to revert due to insufficient balance — a shared-pool insolvency identical in mechanics to the reported Polygon zkEVM bridge issue (X sent, X-fee received, but X committed/promised).

### Impact Explanation
This is a Medium/High severity issue: repeated use of a fee-on-transfer token with this wrapper systematically drains the contract's real token reserve below its committed liabilities. Eventually, legitimate unlock/refund operations for other users of the same underlying token will fail (revert) because the contract lacks sufficient balance, causing a denial-of-service/freezing of funds for unrelated users, and potentially allowing early claimants to drain the shared pool at the expense of later ones.

### Likelihood Explanation
Likelihood is proportional to whether the underlying token configured via `configure()`/`_underlying` is a fee-on-transfer or rebasing/deflationary ERC20. This is entirely permissionless — any unprivileged user can call `send()` with such a token if the owner has configured it as the wrapped underlying, and each call further worsens the shortfall.

### Recommendation
Adopt the same actual-received-amount pattern already used in `IntentGatewayV2.placeOrder` (`evm/src/apps/IntentGatewayV2.sol#L313-L328`): measure `balanceOf(address(this))` before and after `safeTransferFrom`, and use the actual delta as the `amount` encoded into the dispatched message (or explicitly reject/require `received == params.amount` if fee-on-transfer tokens are not intended to be supported).

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` set to a fee-on-transfer token (e.g., 1% transfer fee) via `configure()`.
2. User A calls `send({amount: 1000e18, ...})`. `safeTransferFrom` moves 1000e18 nominally but the contract only receives 990e18 due to the fee.
3. `_buildDispatchPost` encodes `amount: 1000e18` in the message body; this is dispatched and committed cross-chain (or, absent delivery, times out).
4. On timeout, `onPostRequestTimeout` calls `safeTransfer(refundee, 1000e18)` — but the contract only holds 990e18 from this deposit (plus any residual balance from other users), so it must draw the extra 10e18 from other users' locked balances, exactly reproducing the described shared-pool shortfall/DOS.

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
