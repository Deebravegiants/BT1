## Analysis

`WrappedHyperFungibleToken.send()` locks the underlying ERC20 via `safeTransferFrom(msg.sender, address(this), params.amount)` but never checks the actual amount received by the contract. It then encodes `params.amount` (the pre-fee, requested amount) into the cross-chain `Message` and dispatches it. On the destination chain, `HyperFungibleToken.onAccept()` mints `message.amount` to the beneficiary — the full requested amount, not what was actually locked. [1](#0-0) 

Notably, the codebase's `IntentGatewayV2.sol` was explicitly hardened against this exact class of bug — it measures `balanceOf` before/after each `safeTransferFrom` and mutates the order to reflect actual received amounts before computing the commitment, with dedicated tests (`testPlaceOrder_FeeOnTransferToken_*`) proving the pattern. [2](#0-1) [3](#0-2) 

`WrappedHyperFungibleToken.send()` and its upgradeable twin lack this balance-before/after check entirely, and there's no allow-list or check preventing a fee-on-transfer token from being configured as `_underlying` — `configure()` accepts any ERC20 address unconditionally. [4](#0-3) 

### Title
Unbacked minting in WrappedHyperFungibleToken when wrapping fee-on-transfer tokens - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.send()` locks tokens via `safeTransferFrom` but dispatches the cross-chain message with the caller-specified `params.amount` rather than the amount actually received by the contract. If the underlying token charges a transfer fee, the destination `HyperFungibleToken` mints more tokens than were actually escrowed on the home chain, permanently under-collateralizing the wrapper and eventually causing unlock failures for other users.

### Finding Description
In `send()`, the ERC20 branch performs:
```solidity
IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
```
then builds the dispatch message using the same `params.amount` value via `_buildDispatchPost`, without ever comparing balances before/after the transfer. [5](#0-4) 

For a fee-on-transfer underlying token, the wrapper contract only receives `amount * (1 - fee)`, yet the message body claims `amount`. On the destination chain, `HyperFungibleToken.onAccept()` trusts this value and mints the full `message.amount` to the recipient:
```solidity
Message memory message = abi.decode(request.body, (Message));
address beneficiary = _toAddr(message.to);
_mint(beneficiary, message.amount);
``` [6](#0-5) 

This is the same root cause as the referenced Bribe.sol finding — trusting the nominal transfer amount instead of the actually-received balance — but the impact here is stronger: instead of merely locking rewards, it creates an unbacked mint on the remote chain. Each cross-chain transfer through a fee-on-transfer underlying widens the gap between tokens actually locked in `WrappedHyperFungibleToken` and tokens minted as claims on remote chains. Eventually a user bridging back (`send()` on the remote HFT, burning tokens and dispatching a POST that triggers `onAccept`'s `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` on the home chain) will find the wrapper's balance insufficient, reverting delivery and stranding funds/messages. [7](#0-6) 

There is no allow-list check on `configure()` preventing a fee-on-transfer token from being set as `_underlying`. [4](#0-3) 

The identical pattern exists in the upgradeable variant. [8](#0-7) 

### Impact Explanation
This is a Medium/High severity accounting-break bug: it produces an unbacked mint on the destination chain (more wrapped-token claims are minted than the collateral actually escrowed), and progressively insolvency of the `WrappedHyperFungibleToken` contract. Eventually legitimate unlock/refund deliveries revert due to insufficient underlying balance, freezing funds for unrelated users and breaking the token's peg 1:1 assumption across chains. This matches the "unbacked mint" / "permanent freezing of funds" impact categories.

### Likelihood Explanation
Any deployer configuring `WrappedHyperFungibleToken` with a fee-on-transfer, rebasing-on-transfer, or otherwise non-standard ERC20 as the underlying (a scenario the docs don't explicitly forbid) triggers this on every single `send()` call — no attacker action needed beyond a single ordinary bridge transaction. The codebase already demonstrates awareness of and mitigation for this exact bug class in `IntentGatewayV2.sol`, but the fix was not applied to `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable`, indicating an inconsistent/incomplete fix rather than an intentional design choice.

### Recommendation
Mirror the `IntentGatewayV2.sol` pattern: snapshot `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, use the actual delta as the amount encoded in the dispatched `Message` (and emitted in `Sent`), or explicitly document/enforce (e.g., via a check or governance-controlled allow-list) that only standard, non-fee-on-transfer, non-rebasing ERC20 tokens may be configured as `_underlying`.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken`, configure `_underlying` to a token with a 2% transfer fee.
2. User calls `send({amount: 100, to: recipient, dest: remoteChain, ...})`.
3. `safeTransferFrom` pulls 100 but the wrapper's balance only increases by 98 (2% burned in transfer).
4. The dispatched `Message.amount` is still 100; remote `HyperFungibleToken.onAccept` mints 100 tokens to the recipient.
5. Repeat: the wrapper's real underlying balance falls further behind total remote-minted supply.
6. A later `send()` from a remote chain back to home (burn 100, dispatch POST) triggers `onAccept` on `WrappedHyperFungibleToken`, which calls `safeTransfer(beneficiary, 100)` — but the wrapper's actual token balance is insufficient once accumulated shortfalls exceed available balance, reverting delivery and freezing that transfer.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L178-185)
```text
    function configure(WrappedConfigOptions calldata options) external onlyOwner {
        if (_host == address(0)) {
            _host = options.host;
        }
        _dispatcher = options.dispatcher;
        _underlying = options.underlying;
        _isWeth = options.isWeth;
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L234-290)
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

    /**
     * @notice Locks underlying tokens and dispatches a cross-chain transfer message
     * @dev If `_isWeth` is true and msg.value is sufficient, wraps native tokens via the underlying's WETH
     * deposit function (reverts if the underlying is not WETH). The remainder of msg.value
     * after wrapping is forwarded as native payment for dispatch fees.
     *
     * If `_isWeth` is false, locks ERC20 tokens via safeTransferFrom and pays
     * dispatch fees in the host's fee token (pulled from msg.sender).
     *
     * @param params The send parameters including destination, recipient, amount, and optional calldata
     */
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L292-324)
```text
    /**
     * @notice Handles incoming cross-chain token transfer messages
     * @dev Called by the ISMP host when a POST request is received. Verifies the source
     * address matches the configured contract for that chain, then transfers the underlying
     * ERC20 to the recipient. If calldata is present, executes it via the CallDispatcher.
     * @param incoming The incoming POST request containing the token transfer message
     */
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

**File:** evm/src/apps/IntentGatewayV2.sol (L291-306)
```text
            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2441-2494)
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
