Confirmed: `WrappedHyperFungibleToken.send()` and `WrappedHyperFungibleTokenUpgradeable.send()` lock the underlying ERC20 via `safeTransferFrom(msg.sender, address(this), params.amount)` and then dispatch a cross-chain message carrying the *requested* `params.amount` (not the actual amount received), which the destination-chain peer will fully unlock via `safeTransfer(beneficiary, message.amount)`. If `_underlying` is a fee-on-transfer (or rebasing-down) token, the contract receives less than `params.amount`, permanently under-collateralizing the escrow while the ISMP message still commits to the full nominal amount.

### Title
Wrapped HyperFungibleToken lock accounting ignores fee-on-transfer tokens, causing under-collateralized cross-chain mint/unlock - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`, `sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol`)

### Summary
`WrappedHyperFungibleToken.send()` locks `_underlying` tokens with a plain `safeTransferFrom(msg.sender, address(this), params.amount)` and immediately builds the dispatch message body using `params.amount` verbatim, without measuring the contract's actual token balance delta.

### Finding Description
In `send()`: [1](#0-0) 
the ERC20 is pulled via `safeTransferFrom`, but the amount embedded in the dispatched `Message` (via `_buildDispatchPost`) is `params.amount`, the value the caller specified — not the amount actually received: [2](#0-1) 

If `_underlying` charges a transfer fee (or is a rebasing/deflationary token), the contract's balance increases by less than `params.amount`. The ISMP POST request commits to the full `params.amount` regardless. On the destination chain, the peer `onAccept` unconditionally releases the full committed amount to the beneficiary: [3](#0-2) 

This is the same root-cause pattern as the reported finding — trusting a caller-specified `amount` as if it equals the tokens actually received from a `transferFrom` call on an asset that is not guaranteed to be 1:1. The same bug exists in the upgradeable variant: [4](#0-3) 

Notably, the sibling `IntentGatewayV2` contract *does* correctly handle fee-on-transfer tokens by measuring balance-before/after and mutating `order.inputs[i].amount` to the actually-received amount before committing/escrowing: [5](#0-4) 
This confirms the codebase is aware of and defends against this exact class of bug elsewhere, but the `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` bridge apps were not updated with the same balance-delta accounting.

### Impact Explanation
For any deployment where `_underlying` is configured to a fee-on-transfer, deflationary, or rebasing ERC20 (an owner-configurable, non-privileged parameter set via `configure()`), every `send()` call locks strictly less collateral than the amount the destination peer will release. Repeated sends progressively drain the locked-token reserve backing the wrapped asset across all users of that deployment, since later `onAccept` unlocks will pay out more than was ever escrowed — a permanent, protocol-wide shortfall (unbacked unlock) rather than a loss isolated to the single sender. This matches "concrete theft or permanent freezing of funds / unbacked mint" for the bridge's escrow.

### Likelihood Explanation
Triggering requires only that the wrapped `_underlying` token has a non-zero transfer fee or deflationary transfer behavior — a normal, unprivileged ERC20 property that many real-world tokens (e.g., certain stablecoins with fee switches, deflationary/reflection tokens) exhibit. Any single unprivileged `send()` call reaches the vulnerable code path with no special preconditions beyond approving/holding the token, and the destination `onAccept` requires no additional trust assumption beyond normal message delivery.

### Recommendation
In `send()`, measure `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, and use the actual received delta (not `params.amount`) when building the dispatched `Message.amount`, mirroring the pattern already used in `IntentGatewayV2.placeOrder`. Apply the same fix to `WrappedHyperFungibleTokenUpgradeable.send()`.

### Proof of Concept
1. Owner deploys `WrappedHyperFungibleToken` with `_underlying` set to a token that takes a 1% fee on transfer.
2. Alice calls `send()` with `params.amount = 1000`. `safeTransferFrom(alice, this, 1000)` executes, but the contract only receives `990` tokens due to the transfer fee.
3. `_buildDispatchPost` still encodes `amount: 1000` in the `Message` body, and the POST request commits to `1000`.
4. On the destination chain, the peer's `onAccept` calls `IERC20(_underlying).safeTransfer(beneficiary, 1000)` — releasing `10` more tokens than were ever locked.
5. Repeating this across many `send()` calls drains the wrapped-token collateral pool below what is needed to honor legitimate future unlocks, resulting in stuck/insolvent withdrawals for other users.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L312-329)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
        }
```
