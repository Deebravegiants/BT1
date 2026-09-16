### Title
Fee-on-transfer tokens cause unbacked over-minting in `WrappedHyperFungibleToken.send()` - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.send()` locks the underlying ERC20 via `safeTransferFrom` and then dispatches a cross-chain `Message` that credits the caller-supplied `params.amount` verbatim, without verifying that the contract actually received `params.amount` of the underlying token. For fee-on-transfer tokens, the destination `HyperFungibleToken` mints more than what is actually custodied on the home chain, creating an unbacked, permanently growing deficit.

### Finding Description
In `send()`:
```solidity
IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
...
DispatchPost memory request = _buildDispatchPost(params); // body encodes params.amount as-is
``` [1](#0-0) 

`_buildDispatchPost` encodes `params.amount` directly into the cross-chain `Message.amount` field with no adjustment for the actual amount received: [2](#0-1) 

On the destination chain, `HyperFungibleToken.onAccept` mints exactly `message.amount` to the beneficiary (per the burn/mint documentation: "the contract mints new supply to the recipient"), i.e. the amount actually locked on the home chain is never checked against what is minted remotely: [3](#0-2) 

If `_underlying` is a fee-on-transfer token (a fee deducted during `transferFrom`, whether present at configuration time or enabled later by the token's own governance/logic), the wrapper receives `params.amount - fee` but still dispatches a message crediting the full `params.amount`. The destination `HyperFungibleToken` then mints `params.amount`, exceeding the tokens actually locked in `WrappedHyperFungibleToken`. Every subsequent "bridge back" `send()` from the remote chain burns the minted (inflated) balance and expects `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` from the home-chain wrapper — which will eventually fail/run out of underlying balance because the pool is under-collateralized by the accumulated fee amounts. Note the identical `onAccept`/timeout logic (which also `safeTransfer`s `message.amount` without adjustment) is repeated in `WrappedHyperFungibleTokenUpgradeable.sol`: [4](#0-3) 

This is the same bug class flagged in the referenced Cooler audit finding — accounting is performed on the "requested" transfer amount instead of the actual balance delta — and the codebase has already fixed this exact class of issue elsewhere (`IntentGatewayV2.placeOrder`, which explicitly measures `balanceOf` before/after `safeTransferFrom` and mutates `order.inputs[i].amount` to the actual received value, with dedicated fee-on-transfer tests): [5](#0-4) [6](#0-5) 

`WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` never received the equivalent fix.

### Impact Explanation
An unprivileged user calling the public `send()` function with a fee-on-transfer underlying token causes the bridge to mint more tokens on the destination chain than are actually escrowed on the home chain. This is an unbacked-mint condition: over repeated `send()` calls, the shortfall accumulates until the home-chain wrapper can no longer fully honor legitimate "bridge back" redemptions (`onAccept`/timeout `safeTransfer` of `message.amount`), resulting in permanent loss of funds for some users. This satisfies the "unbacked mint" / "permanent freezing of funds" criteria for a valid High-severity finding.

### Likelihood Explanation
Likelihood depends on the owner configuring `_underlying` to a fee-on-transfer (or fee-capable) token. This is plausible without any malicious admin action: many widely used ERC20s (e.g., tokens with governance-controlled transfer taxes, deflationary/reflection tokens) can enable or increase a transfer fee post-deployment, and the wrapper's `configure()` performs no check preventing such tokens from being wrapped. Once configured, exploitation requires nothing more than an ordinary user calling `send()`, i.e. it is fully reachable by an unprivileged token bridger.

### Recommendation
In `WrappedHyperFungibleToken.send()` (and the Upgradeable variant), measure the actual amount received via balance-before/after around `safeTransferFrom`, and encode that actual received amount into the dispatched `Message`, mirroring the pattern already used in `IntentGatewayV2.placeOrder`:
```solidity
uint256 balBefore = IERC20(_underlying).balanceOf(address(this));
IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
uint256 received = IERC20(_underlying).balanceOf(address(this)) - balBefore;
// use `received` instead of params.amount when building the dispatch message
```
Alternatively, explicitly disallow fee-on-transfer/rebasing tokens as `_underlying` at `configure()` time (e.g., by requiring a self-transfer test), consistent with the recommendation given in the referenced Cooler report.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g., 1% fee on `transferFrom`) and configure it as `_underlying` on `WrappedHyperFungibleToken` on the home chain.
2. User calls `send({amount: 1000e18, dest: remoteChain, to: recipient, ...})`.
3. `safeTransferFrom` moves only `990e18` into the wrapper (1% fee retained by token), but `_buildDispatchPost` encodes `amount: 1000e18` in the `Message` body.
4. The ISMP request is delivered to the remote `HyperFungibleToken.onAccept`, which mints `1000e18` to `recipient` — 10e18 more than what is actually locked in the home-chain wrapper.
5. Repeating this drains the wrapper's collateralization ratio; eventually a legitimate "bridge back" `send()` from the remote chain triggers `onAccept`/`safeTransfer` on the home chain that reverts due to insufficient underlying balance, freezing funds for the affected user(s).

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

**File:** docs/content/developers/evm/hyper-fungible-token/hyper-fungible-token.mdx (L8-10)
```text
Deploy this on every **remote chain** where the token doesn't have native supply. The contract inherits from ERC20 and [HyperApp](/developers/evm/api/hyperapp), so it is both the token and the bridge in one contract.

When tokens arrive from the home chain, the contract mints new supply to the recipient. When a user bridges back, it burns their tokens and dispatches an ISMP POST request to the home chain. On timeout, tokens are re-minted to the original sender. The HFT has no initial supply — tokens are only minted when cross-chain transfers arrive.
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L294-324)
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

    /**
     * @notice Handles incoming cross-chain token transfer messages
     * @dev Called by the ISMP host when a POST request is received. Verifies the source
     * address matches the configured contract for that chain, then transfers the underlying
     * ERC20 to the recipient. If calldata is present, executes it via the CallDispatcher.
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2440-2494)
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
    }
```
