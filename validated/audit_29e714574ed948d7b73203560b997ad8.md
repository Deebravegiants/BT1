## Analysis

The bug-class from the external report — accounting for the *requested* transfer amount instead of the *actual* amount received after an ERC20 transfer tax — has a direct, reachable analog in `WrappedHyperFungibleToken`, a cross-chain token bridge contract that locks/unlocks an arbitrary underlying ERC20.

Note that the codebase's own `IntentGatewayV2.placeOrder()` explicitly handles this exact issue for fee-on-transfer tokens by measuring `balanceOf` before/after the transfer and using the *actual* received amount for escrow and commitment purposes [1](#0-0) , and is covered by dedicated tests such as `testPlaceOrder_FeeOnTransferToken_WithProtocolFee` [2](#0-1) . `WrappedHyperFungibleToken` does not apply the same fix.

### Title
Loss of Funds / Bridge Insolvency when `WrappedHyperFungibleToken` wraps Tax-on-Transfer ERC20 tokens - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` locks an arbitrary underlying ERC20 via `safeTransferFrom(msg.sender, address(this), params.amount)` and then dispatches a cross-chain message that encodes `params.amount` (the requested amount) rather than the amount actually received by the contract [3](#0-2) . If the underlying token charges a transfer tax/fee (or ever adds one, e.g. USDT-style tokens), the contract receives less than `params.amount` but still promises the full `params.amount` to be minted/unlocked on the destination chain.

### Finding Description
- In `send()`, the amount locked is whatever the ERC20 `_transfer` actually delivers to the contract, but `_buildDispatchPost()` encodes `message.amount = params.amount` unconditionally [4](#0-3) .
- On the destination chain, `HyperFungibleToken.onAccept()` mints `message.amount` to the beneficiary — the full, untaxed amount [5](#0-4) .
- When those minted tokens are later sent back (`HyperFungibleToken.send()` burns them and dispatches a POST back to the home chain), `WrappedHyperFungibleToken.onAccept()` on the home chain unconditionally calls `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` to release the escrowed underlying [6](#0-5) .
- Because the escrow contract only ever held `amount - tax` per deposit while it is obligated (via minted supply on remote chains) to redeem the full `amount`, the escrow accumulates a shortfall proportional to the cumulative transfer tax across all deposits. Eventually a legitimate unlock (`safeTransfer`) will revert with insufficient balance, permanently freezing funds for whichever user's redemption exhausts the remaining escrow — an unbacked-mint / insolvency condition analogous to the reported "Loss of Funds when using Tax On Transfer ERC20 tokens" issue.
- This is reachable by any unprivileged user calling `send()` with a tax-on-transfer ERC20 configured as `_underlying` — no privileged role is required to trigger the mismatch; the contract owner only configures which token is wrapped, not each individual transfer.

### Impact Explanation
This is a fund-freezing/insolvency bug: the bridge promises (via cross-chain mint) more underlying tokens than it actually escrows. Later legitimate redemptions can revert due to insufficient balance, permanently locking user funds in the destination-chain minted representation or leaving the home-chain escrow unable to honor all outstanding claims. This matches "permanent freezing of funds" / "unbacked mint" criteria.

### Likelihood Explanation
Likelihood depends on the underlying token having (or later adding) a transfer tax/fee, which the contract explicitly claims to support since it accepts an arbitrary `underlying` ERC20 configured by the owner at deployment. Given that the sibling contract `IntentGatewayV2` was already hardened against exactly this scenario (with tests), it indicates fee-on-transfer tokens are an anticipated real-world integration for this codebase, making the likelihood non-negligible for any deployment using such a token as `_underlying`.

### Recommendation
Mirror the `IntentGatewayV2` fix: measure `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom` in `send()`, and use the actual received delta as `message.amount` in the dispatched message body, rather than the raw `params.amount`. Apply the same fix to `WrappedHyperFungibleTokenUpgradeable.send()`, which has identical logic [7](#0-6) .

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` with `_underlying` set to a fee-on-transfer ERC20 (e.g. 1% tax) and configure a peer `HyperFungibleToken` on a destination chain.
2. Call `send({amount: 1000e18, ...})`. The wrapper's `safeTransferFrom` pulls 1000e18 nominally, but the contract's balance only increases by 990e18 due to the tax; `_buildDispatchPost` still encodes `amount: 1000e18`.
3. On the destination chain, `onAccept` mints 1000e18 to the recipient, even though only 990e18 of underlying is actually escrowed on the home chain.
4. Repeat sends to grow the shortfall. When holders of the minted destination-chain tokens burn and bridge back to redeem the underlying, `WrappedHyperFungibleToken.onAccept()`'s `safeTransfer(beneficiary, message.amount)` will eventually revert once cumulative shortfall exceeds the remaining escrowed balance, freezing the last redeemer(s)' funds.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L228-251)
```text
        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2496-2521)
```text
    /// @notice Fee-on-transfer with protocol fees: both deductions applied correctly.
    function testPlaceOrder_FeeOnTransferToken_WithProtocolFee() public {
        IntentGatewayV2 gatewayWithFees = _deployGatewayProxy();
        Params memory intentParams = Params({
            host: address(host),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: SURPLUS_SHARE_BPS,
            protocolFeeBps: PROTOCOL_FEE_BPS, // 30 bps
            priceOracle: address(0)
        });
        gatewayWithFees.initialize(intentParams, new bytes[](0), address(0));

        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% transfer fee
        fot.mint(user, 10000 * 1e18);

        uint256 inputAmount = 1000 * 1e18;
        uint256 receivedAfterTransferFee = inputAmount - (inputAmount * 100) / 10000; // 990
        uint256 protocolFee = (receivedAfterTransferFee * PROTOCOL_FEE_BPS) / 10000;
        uint256 expectedEscrow = receivedAfterTransferFee - protocolFee;

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 900 * 1e18});
```

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L322-324)
```text
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L299-313)
```text
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
