## #Vulnerability found for this question.

### Title
Fee-on-transfer / deflationary underlying tokens cause `WrappedHyperFungibleToken.send()` to dispatch an over-stated locked amount, under-collateralizing the bridge - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` locks the underlying ERC20 via `safeTransferFrom(msg.sender, address(this), params.amount)` and then dispatches a cross-chain message that encodes `params.amount` as the amount to mint/unlock on the destination chain, without ever checking how much the contract's balance actually increased. This is the exact bug class from the external report ("calc swapped amount with difference balance before and after"): if the underlying token takes a fee on transfer (or otherwise delivers less than the nominal amount), the contract locks less than `params.amount` but tells the destination chain that `params.amount` was locked.

### Finding Description
In `send()`, the ERC20-lock branch does: [1](#0-0) 

The contract pulls tokens with `safeTransferFrom(msg.sender, address(this), params.amount)` but never measures `balanceOf(address(this))` before/after the transfer. The subsequently built message body still uses the *requested* `params.amount`, not the amount actually received: [2](#0-1) 

On the destination side, `onAccept` unconditionally transfers/unwraps `message.amount` of the underlying (or WETH) to the beneficiary — the same nominal amount that was claimed to be locked: [3](#0-2) 

The same pattern (missing balance-diff accounting) is duplicated in the upgradeable variant: [4](#0-3) 

By contrast, the codebase's own `IntentGatewayV2` explicitly guards against this exact class of bug by measuring `balanceOf` before and after every ERC20 pull and mutating the persisted/dispatched amount to the actual amount received, e.g.: [5](#0-4) 
This shows the project is aware of and mitigates the fee-on-transfer/balance-diff class elsewhere, but the mitigation was not applied to `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable`, which is the ERC20 lock/unlock token-bridge component reachable directly by any unprivileged user calling `send()`.

### Impact Explanation
This is a token-bridge lock/unlock primitive (in scope per the "token bridge mint/burn" category). If `configure()` is ever pointed at a deflationary/fee-on-transfer/rebasing-down ERC20 as `_underlying` (a permissionless owner decision made once at deployment, and something owners of arbitrary tokens may reasonably want to wrap), every `send()` call locks strictly less than `params.amount` while the destination chain unlocks/transfers the full nominal `params.amount` to the beneficiary. Over repeated sends this creates an ever-growing accounting deficit between the aggregate amount promised across all destination chains and the actual underlying balance held in escrow on the source chain. Eventually redemptions/unlocks on the source chain (via reverse `send()` + `onAccept` unlocking the underlying) will fail for some legitimate holders because the contract's underlying balance is insufficient to back all the tokens that were nominally "minted"/credited elsewhere — a form of unbacked minting/permanent fund freezing for latecomers in the queue. This is a genuine value-theft-adjacent bug (first destination redeemers drain real collateral, leaving later legitimate holders unable to redeem), which corresponds to "unbacked mint" / "permanent freezing of funds" in the accepted impact categories.

### Likelihood Explanation
The precondition is that the token owner configures a fee-on-transfer/deflationary token as `_underlying`. This is plausible: WETH-mode aside, `WrappedHyperFungibleToken` is explicitly designed as a generic "wrapper for existing ERC20 tokens" per its own documentation and README, with no restriction or note against fee-on-transfer tokens, unlike `IntentGatewayV2` which was hardened for exactly this. Any single unprivileged `send()` call triggers the discrepancy — no special conditions, front-running, or governance compromise required once such a token is configured.

### Recommendation
Mirror the mitigation already used in `IntentGatewayV2`: snapshot `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, and use the actual delta as `params.amount` for both the message body dispatched cross-chain and the emitted `Sent` event, in both `WrappedHyperFungibleToken.send()` and `WrappedHyperFungibleTokenUpgradeable.send()`.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` with `configure()` pointing `_underlying` at a mock ERC20 that charges, e.g., a 1% fee on `transferFrom` (as already modeled by `FeeOnTransferToken` in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`).
2. Call `send({ amount: 1000e18, ... })`. The contract's balance only increases by 990e18 (after the 1% fee), verifiable via `mockToken.balanceOf(address(whft))` before/after, analogous to the existing `testSendLocksERC20` test but with a fee-on-transfer token.
3. Observe that the dispatched `Message.amount` inside `_buildDispatchPost` (and the `Sent` event) still equals `1000e18`, not `990e18`.
4. On the destination chain, `onAccept` will unlock/transfer `1000e18` worth of the underlying to the beneficiary even though the source chain only actually escrowed `990e18` — a 10e18 shortfall per send that compounds with repeated transfers, eventually leaving the source-chain contract's escrow balance insufficient to honor legitimate unlocks/refunds for other users.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-324)
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

**File:** evm/src/apps/IntentGatewayV2.sol (L313-323)
```text
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
```
