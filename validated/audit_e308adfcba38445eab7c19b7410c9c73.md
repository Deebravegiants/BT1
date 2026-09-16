## Title
Fee-on-transfer tokens allow unbacked minting/release via `WrappedHyperFungibleToken.send()` ignoring actual received amount - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` (and its identical twin `WrappedHyperFungibleTokenUpgradeable.send()`) locks the underlying ERC20 via `safeTransferFrom` and then dispatches a cross-chain message encoding the user-supplied `params.amount`, without verifying that the contract actually received that amount. If the underlying token charges a transfer fee (deflationary/fee-on-transfer tokens), the contract locks less than `params.amount` but instructs the destination chain to unlock/mint the full `params.amount`, creating a permanent backing shortfall.

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
``` [1](#0-0) 

`_buildDispatchPost` encodes `params.amount` verbatim into the cross-chain `Message`, which is what the peer contract on the destination chain uses in `onAccept` to unlock/transfer the underlying (or mint, for the mint/burn variant of this app family): [2](#0-1) [3](#0-2) 

Since `safeTransferFrom` does not verify the actual balance delta, if `_underlying` deducts a transfer fee, the amount actually locked in the contract (`IERC20(_underlying).balanceOf(address(this))` delta) is strictly less than `params.amount`, yet the full `params.amount` is committed to the ISMP message and will be released/unlocked on the destination chain (or refunded in full on timeout via `onPostRequestTimeout`, which also uses `message.amount`).

The codebase has already recognized and fixed this exact bug class elsewhere: `IntentGatewayV2.sol`'s `placeOrder` explicitly snapshots balances before/after `safeTransferFrom` and mutates `order.inputs[i].amount` to the actually-received amount for exactly this reason:
```solidity
// Phase 1: Transfer tokens and record actual received amounts.
// For fee-on-transfer tokens, the gateway receives less than the requested amount.
...
uint256 balBefore = IERC20(token).balanceOf(address(this));
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
``` [4](#0-3) 

This pattern (and matching fee-on-transfer regression tests) is present in `IntentGatewayV2.sol` and its Tron port, but is absent from `WrappedHyperFungibleToken.sol` / `WrappedHyperFungibleTokenUpgradeable.sol`, which is the exact analog of the FixedFeeSwap bug report: the deposit-crediting side ignores the transfer fee and credits/dispatches the pre-fee amount. [5](#0-4) 

### Impact Explanation
Each `send()` call with a fee-on-transfer underlying token permanently under-collateralizes the wrapper: the destination chain unlocks/refunds the full nominal `params.amount` while the source-chain contract holds less. Repeated over time, this drains the contract's underlying reserve, allowing later callers (or the last redeemers) to be unable to withdraw, and effectively lets earlier senders extract more value than they deposited — a direct, permanent loss/freezing of funds for the bridge's token reserve. This qualifies as unbacked release of value across the bridge, reachable from a single ERC20 `send()` transaction.

### Likelihood Explanation
Requires the operator to configure `_underlying` to a fee-on-transfer/deflationary ERC20 token (via `configure()`), which is plausible for any generically deployed wrapper supporting arbitrary ERC20s, and it is entirely permissionless for any depositor to trigger once such a token is configured — no privileged action needed beyond initial token selection, matching the original report's caveat that tokens "can change" fee behavior at any moment.

### Recommendation
Mirror the fix already applied in `IntentGatewayV2.sol`: measure `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom` in `send()`, and use the actual received delta (not `params.amount`) when building the `Message` that is dispatched cross-chain. Apply the same fix to `WrappedHyperFungibleTokenUpgradeable.send()`.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` = a token that takes a 1% transfer fee (as modeled by `FeeOnTransferToken` in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`).
2. User calls `send({amount: 1000e18, to: recipient, dest: chainB, ...})`.
3. `safeTransferFrom` moves only 990e18 into the contract (1% fee burned/redirected), but `_buildDispatchPost` encodes `amount: 1000e18` in the message body.
4. On chain B, `onAccept` releases/unlocks 1000e18 to the recipient (or, on timeout, `onPostRequestTimeout` refunds the sender 1000e18) even though only 990e18 was ever locked on chain A — a 10e18 shortfall accrues per such transfer, eventually leaving the contract unable to honor other users' locked balances. [6](#0-5)

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-281)
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

**File:** evm/src/apps/IntentGatewayV2.sol (L230-323)
```text
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

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));

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

                unchecked {
                    ++i;
                }
            }
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2690-2735)
```text
contract FeeOnTransferToken {
    string public name = "FeeOnTransferToken";
    string public symbol = "FOT";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    uint256 public feeBps;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor(uint256 _feeBps) {
        feeBps = _feeBps;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        return _transfer(msg.sender, to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        uint256 allowed = allowance[from][msg.sender];
        if (allowed != type(uint256).max) {
            allowance[from][msg.sender] = allowed - amount;
        }
        return _transfer(from, to, amount);
    }

    function _transfer(address from, address to, uint256 amount) internal returns (bool) {
        uint256 fee = (amount * feeBps) / 10_000;
        uint256 received = amount - fee;
        balanceOf[from] -= amount;
        balanceOf[to] += received;
        // fee is burned
        totalSupply -= fee;
        return true;
    }
}
```
