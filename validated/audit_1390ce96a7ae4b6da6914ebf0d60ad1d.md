## Analysis

The reported Teller bug class — accounting collateral/escrow by the *requested* transfer amount instead of the *actually received* amount for fee-on-transfer tokens, causing later withdrawals to be under-collateralized and revert/lock funds — has a direct, unmitigated analog in Hyperbridge's `WrappedHyperFungibleToken` (and its `Upgradeable` twin).

Notably, `IntentGatewayV2.placeOrder` explicitly guards against this exact bug class by measuring `balanceOf` before/after every `safeTransferFrom` and using the *actual received* amount for escrow accounting [1](#0-0) , with dedicated tests confirming correct behavior for fee-on-transfer tokens [2](#0-1) . `WrappedHyperFungibleToken.send`, however, has no such guard.

### Title
Fee-on-transfer underlying token causes under-collateralization and stuck withdrawals in `WrappedHyperFungibleToken` - ([File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol])

### Summary
`WrappedHyperFungibleToken.send()` pulls `params.amount` of the underlying ERC20 via `safeTransferFrom`, but never checks how much was actually received. It then dispatches a cross-chain message carrying the full `params.amount`, which the destination `HyperFungibleToken`/`HyperFungibleTokenUpgradeable` mints in full to the recipient [3](#0-2) . If the underlying token deducts a transfer fee, the wrapper actually custodies less than the amount it has promised (and that has been minted) on remote chains.

### Finding Description
In `send()`:
```solidity
function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
    uint256 msgValue = msg.value;
    if (_isWeth && msgValue >= params.amount) {
        ...
    } else {
        IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
    }
    DispatchPost memory request = _buildDispatchPost(params);
    ...
}
``` [4](#0-3) 

`_buildDispatchPost` embeds `params.amount` — the requested amount, not the amount the wrapper actually received — into the `Message` that is dispatched cross-chain [5](#0-4) . On the destination chain, `HyperFungibleToken.onAccept` mints exactly `message.amount` to the beneficiary [6](#0-5) . If `_underlying` is a fee-on-transfer token, the wrapper's actual balance increase from `safeTransferFrom` is strictly less than `params.amount`, while the destination mints the full `params.amount`. The wrapper is now short by the fee amount relative to the total supply it has backed on other chains.

Symmetrically, `onAccept` for the wrapper unlocks the underlying with `safeTransfer(beneficiary, message.amount)` using the exact `message.amount` decoded from the incoming message, with no allowance for a transfer fee taken on the outbound leg either [7](#0-6) . Every `send()` call widens a shortfall between (a) the wrapper's real token balance and (b) the amount promised/minted for that token across all remote-chain `HyperFungibleToken` deployments.

This is the same root-cause class as the reported Teller issue: recording the pre-transfer-fee amount instead of the post-transfer-fee (`after - before` balance) amount when custodying tokens that will later be paid back out 1:1.

The upgradeable variant has the identical pattern [8](#0-7) .

### Impact Explanation
Once the shortfall accumulates (through repeated `send()` calls with a fee-on-transfer underlying, or even a single call with a high enough fee), a legitimate user attempting to bridge tokens back and unlock via `onAccept`/`onPostRequestTimeout` can hit a `safeTransfer` that reverts because the wrapper's actual balance is less than the sum of all outstanding minted supply. This is a permanent freezing-of-funds condition: subsequent redeemers may find their unlock transactions revert, and there is no recovery path in the contract (no `afterBalance - beforeBalance` accounting, no reconciliation mechanism). This matches the "permanent freezing of funds" / "unbacked mint" impact classes.

### Likelihood Explanation
Reachable by any unprivileged user simply calling `send()` with a fee-on-transfer ERC20 configured as the wrapper's `underlying` — no privileged role required. Given that `WrappedHyperFungibleToken` is a generic wrapper meant to support "existing ERC20 tokens" per its own documentation (not restricted to a known-safe allowlist) [9](#0-8) , deployment against a fee-on-transfer token is a realistic operational scenario, and the codebase already demonstrates elsewhere (`IntentGatewayV2`) that this exact risk is understood and normally mitigated — just not here.

### Recommendation
In `WrappedHyperFungibleToken.send()` (and the `Upgradeable` variant), measure `balanceOf(address(this))` before and after `safeTransferFrom`, and use the actual delta as the amount encoded in the dispatched `Message` and used for accounting, mirroring the pattern already implemented in `IntentGatewayV2.placeOrder` [1](#0-0) .

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` configured with a fee-on-transfer ERC20 (e.g., 1% fee) as `underlying`.
2. User calls `send({ amount: 1000e18, ... })`. `safeTransferFrom` pulls 1000e18 but the wrapper only receives 990e18 (10e18 lost to the token's fee) — `send` still dispatches a `Message` with `amount: 1000e18` [4](#0-3) .
3. Destination-chain `HyperFungibleToken.onAccept` mints 1000e18 to the recipient [6](#0-5) .
4. The wrapper now holds 990e18 but has backed 1000e18 of remote supply — a 10e18 shortfall.
5. Repeat step 2 with more users/sends until the wrapper's actual balance is less than an amount some user needs to redeem back on the home chain; that user's bridge-back `onAccept` unlock call reverts on `safeTransfer` due to insufficient balance, permanently blocking their withdrawal (analogous to the `CollateralEscrowV1.withdraw()` revert in the original report).

### Citations

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2440-2493)
```text
    /// @notice Escrow correctly reflects actual received amount for fee-on-transfer tokens.
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

        // Reconstruct the order as placeOrder would have mutated it
        order.user = bytes32(uint256(uint160(user)));
        order.source = host.host();
        order.nonce = 0;
        order.inputs[0].amount = expectedReceived;
        bytes32 commitment = keccak256(abi.encode(order));

        // Escrow should match actual received, not the user-specified amount
        assertEq(
            intentGateway._orders(commitment, address(fot)),
            expectedReceived,
            "Escrow should equal actual received amount"
        );
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-301)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);
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

**File:** docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx (L1-10)
```text
---
title: WrappedHyperFungibleToken
description: Deploying and configuring lock/unlock WrappedHyperFungibleToken contracts on the home chain.
---

# WrappedHyperFungibleToken

Deploy this on the token's **home chain** where the canonical ERC20 supply lives. The wrapper custodies the underlying token without minting any new supply — it locks tokens when users bridge out and unlocks them when users bridge back. No pre-funding is required.

For WETH wrappers (`isWeth = true`), users can send native ETH/BNB directly via `msg.value` and the contract wraps it automatically. On receive, the contract unwraps WETH and sends native tokens to the recipient. On timeout, the contract unwraps and refunds native tokens.
```
