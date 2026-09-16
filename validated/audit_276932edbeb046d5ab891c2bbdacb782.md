### Title
`IntentGatewayV2.placeOrder` (Tron variant) credits escrow with the nominal input amount instead of the token amount actually received, unlike the mainline EVM contract - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2.placeOrder` transfers ERC20 input tokens via `safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then credits `_orders[commitment][token]` with `reducedInputs[i].amount` — a value derived purely from the caller-supplied `order.inputs[i].amount` — without ever checking the gateway's actual token balance before/after the transfer. This is the same root-cause pattern as the reported bug class: the contract assumes the token amount it holds equals a value taken at face value rather than the value actually received, so any deviation between "declared" and "received" (fee-on-transfer tokens, rebasing tokens, tokens with transfer hooks) causes escrow accounting to diverge from real custody.

### Finding Description
In the mainline EVM `IntentGatewayV2.sol`, the non-predispatch input-transfer path explicitly measures actual received tokens: [1](#0-0) 
This balance-before/balance-after pattern is exactly what the fee-on-transfer tests validate: [2](#0-1) 

However, the Tron contract's equivalent non-predispatch branch skips this measurement entirely and stores the nominal amount: [3](#0-2) 

Here, `reducedInputs[i].amount` is computed earlier purely from `order.inputs[i].amount` (the value the caller declares), before any transfer occurs: [4](#0-3) 

So for any ERC20 whose `transferFrom` delivers less than the requested amount (fee-on-transfer, deflationary, or rebasing tokens), the gateway credits the order's escrow ledger (`_orders[commitment][token]`) with more than it actually holds. This is the direct analog of the fsGLP/sGLP report: the contract accounts for a token amount that does not correspond to what it physically received, producing systematically incorrect internal bookkeeping.

### Impact Explanation
Because `_orders[commitment][token]` is over-credited relative to actual custody, a solver who later fills the order and calls the withdrawal path (`_withdraw` in `IntentsBase.sol`) can be released the escrowed amount recorded in `_orders`, which exceeds the gateway's true token balance for that asset. In a multi-order contract holding many users' escrowed tokens concurrently, this can be exploited to drain tokens belonging to other unrelated orders once the shortfall is realized (a token controlled by any actor able to configure or select such an asset as `order.inputs[i].token`), or it can permanently strand the affected order's counterpart output since the promised input can never be fully paid out — a freezing-of-funds condition. This matches the required class of "concrete theft or permanent freezing of funds" reachable from a single submitted transaction (`placeOrder`).

### Likelihood Explanation
Reachable directly and unconditionally by any user calling `placeOrder` with any input token, with no privileged role required. It is triggered automatically whenever the chosen ERC20 input token does not deliver the full nominal amount on `transferFrom` (fee-on-transfer/deflationary/rebasing tokens are common in the wild and nothing in this contract path restricts token choice). The fact that the sibling EVM contract explicitly hardens against exactly this scenario (with dedicated tests) confirms this is a known-required invariant that the Tron variant fails to preserve.

### Recommendation
Mirror the mainline EVM logic in `evm/src/apps/IntentGatewayV2.sol` lines 312-329: in the Tron `IntentGatewayV2.placeOrder` non-predispatch branch, snapshot `IERC20(token).balanceOf(address(this))` before `safeTransferFrom`, compute the actual received delta afterward, and use that measured value (after protocol fee reduction) — not the caller-declared `order.inputs[i].amount` — when computing `reducedInputs`, the commitment hash, and the `_orders[commitment][token]` credit.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g., 1% fee) as in `FeeOnTransferToken` from the test suite. [5](#0-4) 
2. User calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs[0] = {token: FOT, amount: 1000e18}`.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` actually delivers only `990e18` to the gateway due to the transfer fee.
4. `_orders[commitment][FOT] += reducedInputs[0].amount` credits `1000e18` (minus protocol fee if any) — i.e., an amount the gateway never actually received.
5. When a solver fills the order and the escrow is later released via `_withdraw`, the gateway attempts to pay out more `FOT` than its actual balance for that token, either reverting (freezing the order/solver funds) or, in a shared-liquidity scenario, paying out of other users' escrowed `FOT` balances (theft).

### Citations

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2440-2479)
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
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2689-2730)
```text
/// @dev ERC20 with a configurable transfer fee (in basis points).
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-385)
```text
        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            // Temporarily swap inputs to calculate commitment with reduced amounts
            TokenInfo[] memory originalInputs = order.inputs;
            order.inputs = reducedInputs;
            commitment = keccak256(abi.encode(order));
            order.inputs = originalInputs;
        } else {
            // No protocol fees, use order.inputs directly
            reducedInputs = order.inputs;
            commitment = keccak256(abi.encode(order));
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```
