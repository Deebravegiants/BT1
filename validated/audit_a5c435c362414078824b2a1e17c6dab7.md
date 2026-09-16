## Analysis

The reported bug class — an entry point that performs a low-level call/delegatecall to an attacker-influenced target with attacker-influenced calldata, without validating either — maps to `CallDispatcher.dispatch()` in the Hyperbridge EVM apps.

### Title
Unauthenticated `CallDispatcher.dispatch()` allows anyone to drain funds left in the dispatcher by cross-chain calldata execution - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` is `external` with **no access control whatsoever** — no `onlyHost`, no owner check, not even a check that the caller is one of the apps that use it (`HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`/`IntentsBase`). It decodes an arbitrary `Call[]` and executes each `to.call{value: call.value}(call.data)` using the dispatcher's own balance, exactly like the unvalidated `_init`/`_calldata` pattern in the referenced report, except here it's a plain `call` reachable by any transaction, not even gated behind a privileged role. [1](#0-0) 

### Finding Description
`CallDispatcher` is deployed once per app (e.g. one per `HyperFungibleToken` deployment via `DeployHFT.s.sol`) and is used as a temporary holder of bridged funds during composable execution: on `onAccept`, tokens are minted/unlocked to a beneficiary — which callers are free to set to the `CallDispatcher` address itself — and then the sender-supplied `data` field (an ABI-encoded `Call[]`) is forwarded to `dispatch()` to perform swaps, approvals, deposits, etc. [2](#0-1) 

The same pattern exists in `WrappedHyperFungibleToken.onAccept` and in `IntentsBase._execute`, all of which delegate arbitrary-call execution to this same unrestricted `dispatch()` function: [3](#0-2) [4](#0-3) 

Because the sender fully controls the `data`/`order.output.call` payload (it is only ABI-decoded, never checked against an expected shape or amount), any bridged amount that isn't perfectly consumed by the encoded `Call[]` (e.g., slippage on a swap, a partial approval, a call that reverts mid-batch of a differently structured payload, or simply a sender choosing not to fully spend it) remains as a real ERC20/native balance sitting in the `CallDispatcher` contract after the transaction completes. `IntentsBase._execute` recognizes this risk and explicitly sweeps residual balances back to itself after `dispatch()` returns, but `HyperFungibleToken.onAccept` and `WrappedHyperFungibleToken.onAccept` perform **no such sweep** — any leftover balance is simply left in the dispatcher. [5](#0-4) 

Since `dispatch()` has no caller restriction, any unprivileged actor (relayer, solver, or arbitrary EOA) can call `CallDispatcher.dispatch()` directly — not through any app contract — supplying a `Call` that transfers out whatever ERC20/native balance currently sits in the dispatcher to themselves, stealing funds left there by a previous legitimate cross-chain delivery.

### Impact Explanation
Concrete theft of user/protocol funds: any residual balance transiently or permanently held by a `CallDispatcher` instance (due to imperfect spend of bridged funds during calldata execution, or the receive() function accepting stray ETH) can be swept by any third party, since the dispatch function that moves the dispatcher's balance is fully public and unauthenticated.

### Likelihood Explanation
High for any deployment where senders route bridged funds through the `CallDispatcher` for composable execution (explicitly documented and demonstrated in the HFT docs and tests) and the destination call doesn't consume the entire minted/unlocked amount — a very plausible outcome for swaps with slippage or multi-step compositions. No proof, no signature, and no privileged role is required to exploit it; a single call to the already-known, publicly deployed `CallDispatcher` address suffices.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the app contract(s) that own it (e.g. an `onlyOwner`/allow-listed-caller check set at construction), and/or make the balance-bearing apps (`HyperFungibleToken`, `WrappedHyperFungibleToken`) sweep any residual dispatcher balance back to the beneficiary in the same transaction, mirroring what `IntentsBase._execute` already does.

### Proof of Concept
1. A user calls `HyperFungibleToken.send()` on the source chain with `SendParams.to = address(callDispatcher)` and `data` encoding a `Call[]` that performs a swap which doesn't fully consume the bridged amount (e.g., due to slippage).
2. On the destination chain, `onAccept` mints the full amount to `callDispatcher`, then calls `ICallDispatcher(dispatcher).dispatch(message.data)`, which executes the swap, leaving leftover tokens in `callDispatcher`. [6](#0-5) 
3. Any attacker, in the same or a later block, calls `CallDispatcher.dispatch(encoded)` directly with a `Call{to: leftoverToken, data: transfer(attacker, leftoverBalance)}`, draining the residual funds — no authentication is checked anywhere in `dispatch()`. [7](#0-6)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-62)
```text
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
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
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-328)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L504-533)
```text
        Call[] memory sweepCalls = new Call[](outputsLen);
        uint256 sweepCount = 0;

        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

            if (token == address(0)) {
                uint256 balance = dispatcher.balance;
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({to: address(this), value: balance, data: ""});
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            } else {
                uint256 balance = IERC20(token).balanceOf(dispatcher);
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            }

            unchecked {
                ++i;
            }
        }
```
