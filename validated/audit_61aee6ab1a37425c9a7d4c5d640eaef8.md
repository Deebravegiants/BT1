Confirmed: both `WrappedHyperFungibleToken.sol` and `WrappedHyperFungibleTokenUpgradeable.sol` share the same unguarded `safeTransferFrom` pattern with no balance-before/after measurement, unlike `IntentGatewayV2.sol` which explicitly handles fee-on-transfer tokens.

### Title
Fee-on-transfer / reflection token accounting mismatch in cross-chain lock leads to unbacked mint and insolvent escrow - ([File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol])

### Summary
`WrappedHyperFungibleToken.send()` locks an underlying ERC20 by calling `safeTransferFrom(msg.sender, address(this), params.amount)` and then dispatches a cross-chain `Message` that declares the full `params.amount` as the value to credit on the destination chain, without ever measuring how much the contract actually received. [1](#0-0) 

### Finding Description
For deflationary/reflection/fee-on-transfer ERC20s (the same token class exploited in the "Sheep" report, where `burn()`/transfer side effects change realized balances), `IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount)` can deliver strictly less than `params.amount` to the contract. `_buildDispatchPost` still encodes `params.amount` unmodified into the outgoing `Message.amount`: [2](#0-1) 

This is the exact class of bug the codebase already defends against elsewhere: `IntentGatewayV2.placeOrder` explicitly snapshots balances before/after transfers and mutates `order.inputs[i].amount` to the *actual* received amount specifically to handle fee-on-transfer tokens, as shown by its dedicated test suite (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, etc.). [3](#0-2) [4](#0-3) 

`WrappedHyperFungibleToken` (and its upgradeable twin) never applies this fix. On the receiving side, `onAccept` unconditionally transfers out `message.amount` of the underlying to the beneficiary: [5](#0-4)  — and `onPostRequestTimeout` refunds `message.amount` the same way. [6](#0-5) 

Because every `send()` under-collateralizes the escrow by the token's transfer-fee/reflection delta while every `onAccept`/timeout-refund pays out the full nominal amount, the contract's underlying balance is systematically drained faster than deposits replenish it. This is reachable by any unprivileged user who simply calls `send()` with a fee-on-transfer or reflection underlying token — no privileged role or governance action is required.

### Impact Explanation
Repeated `send()` calls with such an underlying token create a growing shortfall between the aggregate `message.amount` values dispatched across chains (which mint/unlock at face value on the other side) and the actual underlying tokens escrowed on the sending chain. Eventually, legitimate `onAccept` unlocks or `onPostRequestTimeout` refunds will fail (revert due to insufficient balance) or, if front-run, allow certain users to withdraw more underlying than the aggregate deposits back them — a form of unbacked mint/theft and permanent freezing of funds for later users, since `WrappedHyperFungibleToken` operates without a shared custody buffer beyond what `send()` actually locked.

### Likelihood Explanation
Likelihood depends on whether an owner configures `_underlying` to a fee-on-transfer, reflection, or otherwise balance-mutating token (common in ecosystems bridging arbitrary ERC20s, as this contract is explicitly designed to wrap "existing ERC20 tokens"). Given the contract's own documentation states it wraps "existing ERC20 tokens" generically, and the project already had to special-case this exact issue in `IntentGatewayV2`, the risk is realistic wherever an integrator points `WrappedHyperFungibleToken` at a non-standard token.

### Recommendation
Mirror the `IntentGatewayV2` pattern in `WrappedHyperFungibleToken.send()`: snapshot `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, and dispatch the *actual received delta* as `Message.amount` instead of `params.amount`. Apply the same fix to `WrappedHyperFungibleTokenUpgradeable.sol`.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` set to a fee-on-transfer/reflection token (e.g., a token charging 1% on every transfer, analogous to SHEEP in the report).
2. Attacker (or any user) calls `send({amount: 1000e18, to: attackerOnDestChain, dest: chainB, ...})`. The contract's `safeTransferFrom` only nets ~990e18 actually escrowed, but the dispatched `Message.amount` is `1000e18`. [7](#0-6) 
3. On chain B, the peer contract mints/unlocks 1000e18 to the attacker (full nominal value, no fee deduction, since chain B's token isn't necessarily fee-on-transfer).
4. Attacker repeats/scales this operation; chain A's actual underlying balance shrinks by the fee percentage each round while nominal committed liabilities on chain B never shrink, eventually leaving chain A's `WrappedHyperFungibleToken` unable to honor `onAccept` unlocks or `onPostRequestTimeout` refunds for other users — draining/freezing funds.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L318-323)
```text
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2441-2479)
```text
    function testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived() public {
        // Deploy a 1% fee-on-transfer token
        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% = 100 bps
        fot.mint(user, 10000 * 1e18);

        uint256 inputAmount = 1000 * 1e18;
        uint256 expectedReceived = inputAmount - (inputAmount * 100) / 10000; // 990

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 900 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 100,
            nonce: 0,
            fees: 0,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        fot.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        // Gateway should hold only what it actually received
        assertEq(
            fot.balanceOf(address(intentGateway)), expectedReceived, "Gateway balance should match received amount"
        );
```
