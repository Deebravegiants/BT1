Confirmed: `WrappedHyperFungibleToken.send()` locks `params.amount` via `safeTransferFrom` but does not verify how much was actually received before dispatching a message that instructs the peer to mint/unlock the full `params.amount` on the destination chain.

### Title
Unbacked mint from fee-on-transfer/deflationary underlying tokens in `WrappedHyperFungibleToken.send()` - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.send()` pulls `params.amount` from the caller with `safeTransferFrom` and then dispatches a cross-chain message carrying that same `params.amount`, without checking the token balance actually credited to the contract. If the configured `_underlying` token charges a transfer fee or otherwise delivers less than requested, the locked collateral backing the bridged token falls below what the message promises the destination chain — mirroring the reserve-shortfall bug class from the external report, where a withdrawal path removes funds without verifying that what remains still backs outstanding claims.

### Finding Description
In `send()`:
```
sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol:266-290
``` [1](#0-0)  the ERC20 branch calls `safeTransferFrom(msg.sender, address(this), params.amount)` and then immediately builds the dispatch message with the *requested* `params.amount` [2](#0-1) , not the actual balance delta. This is unlike `IntentGatewayV2.placeOrder()`, which explicitly measures `IERC20(token).balanceOf(address(this))` before and after the transfer and reduces `order.inputs[i].amount` to the actually-received amount to keep escrow and commitment consistent with real custody [3](#0-2) . `WrappedHyperFungibleToken` has no such reconciliation.

On the destination chain, `onAccept()` decodes `message.amount` from the dispatched body and mints (for `HyperFungibleToken`, via `_mint`) or unlocks (for another `WrappedHyperFungibleToken`, via `safeTransfer`) exactly that amount [4](#0-3) . Because the home-chain lock leg under-collects (fee-on-transfer) while the destination leg mints/unlocks the full requested amount, the locked balance on the home chain (the sole backing for the token's cross-chain circulating supply) becomes permanently insufficient to redeem all outstanding claims — directly analogous to Unitas's `sendPortfolio()` removing collateral without verifying remaining reserves stay solvent for redemptions.

This is reachable by any unprivileged user in a single transaction: simply call `send()` against a `WrappedHyperFungibleToken` instance whose owner has configured a deflationary/fee-on-transfer underlying token. No governance or admin action is required to trigger the shortfall — only the initial (owner-controlled) choice of underlying token, which is a normal, expected configuration step, not an attack by the owner.

### Impact Explanation
The shortfall accumulates with every `send()` call against a fee-on-transfer underlying, so the home-chain custody balance drifts further below the total amount represented as minted/unlocked-eligible supply on remote chains. Eventually, legitimate users attempting `onAccept`-triggered unlocks (bridging back) or timeout refunds will find `IERC20(_underlying).safeTransfer(...)` reverting due to insufficient balance, causing a subset of users to have their bridged funds permanently frozen — an unbacked-mint / permanent-freezing-of-funds condition affecting unprivileged bridge users, not just the party who triggered the drift.

### Likelihood Explanation
Likelihood depends on the underlying token having a fee-on-transfer, rebasing, or otherwise non-standard transfer semantics. The contract imposes no restriction preventing such tokens from being configured, and the `send()` path performs no post-transfer balance check to guard against it, unlike the sibling `IntentGatewayV2` contract which explicitly guards this exact class of token behavior. Given that `WrappedHyperFungibleToken` is a generic, permissionless template meant to wrap "existing ERC20 tokens" (per its own docs), deployers wrapping arbitrary/community tokens with such transfer mechanics is a realistic scenario, and exploitation requires no special privilege once such a token is configured.

### Recommendation
In `send()`, measure `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, and use the actual received delta as the dispatched `params.amount` (and in the `Sent` event), consistent with the pattern already used in `IntentGatewayV2.placeOrder()`. Alternatively, explicitly document and enforce a restriction against configuring underlying tokens with fee-on-transfer or rebasing behavior.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` and configure `_underlying` to a mock ERC20 that charges a 5% fee on transfer (deducted from `transferFrom`).
2. A user calls `send(SendParams{ amount: 1000e18, dest: <remote chain>, to: <recipient>, ... })`.
3. `safeTransferFrom` moves only 950e18 into the contract (5% fee burned/redirected), but `send()` still dispatches a message with `amount: 1000e18` [5](#0-4) .
4. On the destination `HyperFungibleToken`, `onAccept()` mints 1000e18 to the recipient [6](#0-5) .
5. The home-chain wrapper now holds only 950e18 of underlying but backs 1000e18 of minted remote supply — a 50e18 shortfall. Repeating this widens the gap until a `safeTransfer` in `onAccept`/`onPostRequestTimeout` on the home chain reverts for insufficient balance, freezing a later user's funds.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L312-323)
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
