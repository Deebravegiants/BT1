### Title
Fee-on-Transfer / Non-Standard ERC20 Underlying Causes Escrow Under-Collateralization in WrappedHyperFungibleToken - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol)

### Summary
`WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` lock an underlying ERC20 in escrow on the source chain and dispatch a cross-chain message instructing the destination chain to release the same nominal `params.amount` to the recipient. The `send()` function trusts `params.amount` as the amount actually escrowed, rather than measuring the real balance change from `safeTransferFrom`. This is the same root cause as the referenced Gearbox `PoolService.sol` "incorrect minting" report: fee-on-transfer / deflationary ERC20 tokens deliver less than `amount` to the contract, but the protocol credits the full `amount` downstream.

### Finding Description
In `send()`, the contract pulls the underlying token from the caller with `safeTransferFrom` and then builds the cross-chain dispatch body using the caller-supplied `params.amount`, not the observed balance delta: [1](#0-0) 

`_buildDispatchPost` embeds `params.amount` directly into the `Message.amount` field that is sent to the destination chain: [2](#0-1) 

On the destination chain, `onAccept` decodes that message and releases/mints the full `message.amount` to the beneficiary without any verification that the source-chain escrow actually received that amount: [3](#0-2) 

If the underlying ERC20 configured for a `WrappedHyperFungibleToken` deployment applies a transfer fee, rebase, or any deduction (fee-on-transfer, e.g., USDT-style fee switch, or a rebasing/deflationary token), `safeTransferFrom(msg.sender, address(this), params.amount)` will increase the contract's actual token balance by less than `params.amount`, while the dispatched message still commits to releasing the full nominal `params.amount` on the destination side (or refunding the full amount via `onPostRequestTimeout`, which calls `_mint(refundee, message.amount)`).

### Impact Explanation
Each cross-chain transfer of such a token under-collateralizes the escrow by the fee amount while promising full-value delivery on the destination. Because the escrow is shared custody for all users of that deployment, this creates a growing shortfall: multiple sends compound the deficit until the escrow can no longer honor withdrawals/redemptions for legitimate users, i.e., a permanent, protocol-level fund-shortfall/insolvency in the bridge's shared custody pool — an unbacked release of tokens on the destination chain relative to what is actually locked on the source. This is reachable by any unprivileged user simply by calling `send()` with a token that has non-standard transfer semantics.

### Likelihood Explanation
Likelihood depends on whether a deployment's `_underlying` token has fee-on-transfer, rebasing, or deflationary behavior — the code contains no allow-list/validation preventing configuration of such tokens, and no check that the received balance matches `params.amount`. Any owner deploying `WrappedHyperFungibleToken` against a token with transfer fees (now common, e.g., USDT fee-switch tokens, some deflationary/rebasing tokens) exposes every user of that deployment to gradual escrow depletion, triggered by ordinary, unprivileged `send()` calls — no special privileges or timing needed.

### Recommendation
Measure the actual balance received rather than trusting `params.amount`: read `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, and use the balance delta as the amount encoded in the dispatched `Message` (and as the amount refunded on timeout). Alternatively, explicitly document/enforce that only standard, non-fee-on-transfer, non-rebasing ERC20s may be configured as `_underlying` for this contract, and add a runtime check that reverts if the received balance is less than `params.amount`.

### Proof of Concept
1. Deploy `WrappedHyperFungibleTokenUpgradeable` with `_underlying` set to a fee-on-transfer ERC20 (e.g., a token that deducts 1% on every transfer).
2. User A calls `send(params)` with `params.amount = 1000`. `safeTransferFrom` moves only 990 tokens into the contract (10 lost to fee), but the dispatched `Message.amount` is still `1000`.
3. On the destination chain, `onAccept` mints/releases `1000` to the recipient.
4. Repeat across multiple users/sends: the escrow on the source chain accumulates a growing deficit between what is actually held and what has been promised/released on destination chains, eventually preventing legitimate redemptions/unlocks for other users of the same deployment.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L271-285)
```text
        );

        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }

    /**
     * @notice Locks underlying tokens and dispatches a cross-chain transfer message
     * @dev If `_isWeth` is true and msg.value is sufficient, wraps native tokens via the underlying's WETH
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-336)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
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

        emit Received({from: message.from, to: beneficiary, source: string(request.source), amount: message.amount});
    }
```
