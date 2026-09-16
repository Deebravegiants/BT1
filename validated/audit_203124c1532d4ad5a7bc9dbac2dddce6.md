### Title
Fee-on-transfer tokens cause locked-collateral shortfall and over-refund in `WrappedHyperFungibleToken` cross-chain token bridge - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.send()` locks the underlying ERC20 via `safeTransferFrom` and then dispatches a cross-chain message encoding the caller-specified nominal `params.amount`, without measuring the amount actually received by the contract. If `_underlying` is a fee-on-transfer token, the contract locks less than `params.amount` while the dispatched message — and therefore the destination chain's unlock/mint and the timeout refund — always use the untouched nominal `params.amount`. This is the same bug class as the referenced Sherlock finding for Union Finance's `UserManager`, and the codebase's own `IntentGatewayV2` contracts show the project is aware of and specifically hardened for this class of bug (balance-before/after diffing), but `WrappedHyperFungibleToken` (and its upgradeable twin) were not hardened.

### Finding Description
In `send()`:
```solidity
IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
...
DispatchPost memory request = _buildDispatchPost(params); // encodes params.amount, unmodified
``` [1](#0-0) 

`_buildDispatchPost` embeds the raw `params.amount` into the cross-chain `Message`: [2](#0-1) 

On the receiving side, `onAccept` unconditionally transfers `message.amount` (the nominal, unadjusted amount) out of the destination chain's own underlying token reserve to the beneficiary: [3](#0-2) 

And `onPostRequestTimeout` refunds the same unadjusted `message.amount` from the contract's own locked pool back to the original sender: [4](#0-3) 

Because none of these three paths measure `balanceOf(address(this))` before/after the transfer (unlike `IntentGatewayV2.placeOrder`, which explicitly does `balBefore`/`balanceOf` diffing specifically to defend against fee-on-transfer tokens, see `evm/src/apps/IntentGatewayV2.sol` lines 312-328 and the dedicated `FeeOnTransferToken` tests in `IntentGatewayV2SameChainTest.sol`), any fee-on-transfer underlying token creates a persistent shortfall between what is actually escrowed on the source chain and what is claimed/unlocked on the destination chain (or refunded on timeout). Every `send()` call with such a token silently under-collateralizes the bridge by the transfer-fee amount, while destination-side unlocks and timeout refunds continue to pay out the full nominal amount from the shared underlying reserve.

The identical unguarded pattern exists in `WrappedHyperFungibleTokenUpgradeable.sol`'s `send()`: [5](#0-4) 

### Impact Explanation
This is a token-bridge mint/burn (lock/unlock) accounting flaw. Each `send()` call with a fee-on-transfer underlying token leaves the source-chain contract holding strictly less than the amount it commits to release on the destination chain (or refund on timeout). Over repeated transfers, the aggregate underlying reserve backing the bridge becomes insolvent relative to the aggregate amount the bridge has promised to pay out across `onAccept` and `onPostRequestTimeout` calls. Eventually, legitimate unlock or refund calls for other users will fail or drain reserve meant for other pending transfers, resulting in permanent loss/freezing of bridged funds for some users — a direct instance of "unbacked mint" / "concrete theft or permanent freezing of funds" as defined in scope.

### Likelihood Explanation
Likelihood depends entirely on whether a deployment configures `_underlying` to a fee-on-transfer ERC20 token (deflationary/tax tokens are common in practice, e.g., certain reflection or tax tokens). The contract exposes `configure()` (owner-controlled) to set an arbitrary `_underlying` address with no restriction against fee-on-transfer semantics, and `send()` is callable by any unprivileged user once configured. Any user transacting with such an underlying triggers the shortfall on every single call — no special conditions or race are required, only an underlying token whose `transferFrom` delivers less than the requested amount.

### Recommendation
In `send()`, measure the actual amount received via balance-before/after (as already done in `IntentGatewayV2.placeOrder`) and encode that measured amount into the dispatched `Message` instead of the raw `params.amount`. Alternatively, explicitly document/enforce (e.g., via a allowlist check or revert) that fee-on-transfer tokens are unsupported as the `underlying` for `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable`.

### Proof of Concept
1. Owner calls `configure()` setting `_underlying` to a fee-on-transfer ERC20 with, say, a 1% transfer fee, and `_isWeth = false`.
2. Alice calls `send({amount: 1000e18, dest: chainB, ...})`. `safeTransferFrom` pulls 1000e18 from Alice but the contract's `_underlying` balance only increases by 990e18 (10e18 lost to the token's fee) — see `send()` at `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol` line 272.
3. The dispatched `Message.amount` is still `1000e18` (`_buildDispatchPost`, line 241).
4. On chain B, `onAccept` unlocks/transfers `1000e18` of the underlying to the beneficiary from chain B's reserve (line 323), even though chain A's reserve only grew by 990e18.
5. Repeating this pattern across many transfers accumulates a growing shortfall between chain-A-locked collateral and the cumulative amount chain B has unlocked, until chain B's reserve cannot honor further legitimate unlocks/refunds for other users — permanent fund loss/freezing.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-289)
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L294-300)
```text
    function send(HyperFungibleTokenUpgradeable.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
```
