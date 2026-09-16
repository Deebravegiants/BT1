### Title
Fee-on-transfer input tokens desynchronize escrow accounting from actual token balance in Tron `IntentGatewayV2.placeOrder` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits order escrow using the user-declared input amount (minus protocol fee) rather than the amount the contract actually receives after `safeTransferFrom`. For any ERC20 input token that charges a fee on transfer, the escrow ledger (`_orders[commitment][token]`) will record more tokens than the contract's real balance, creating an insolvency that can be exploited to drain funds belonging to other orders/users.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `placeOrder` computes `reducedInputs[i].amount` purely from `order.inputs[i].amount` (the caller-declared amount) and the protocol fee, and this reduced value both feeds the commitment hash and is unconditionally added to escrow accounting: [1](#0-0) 

For the direct-transfer path (no predispatch calldata), the contract pulls tokens with `safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then blindly credits `_orders[commitment][token] += reducedInputs[i].amount`, without ever comparing the requested amount to the balance actually received: [2](#0-1) 

Even the predispatch/sweep path only checks that the swept `balance >= requiredAmount` and still credits the escrow with the *declared* `reducedInputs[i].amount`, not the amount actually swept in minus fees: [3](#0-2) 

This is precisely the bug class from the referenced report: any token that deducts a transfer fee (present or future USDT/USDC-style deployments, or any token later listed as collateral/input) causes the contract to hold strictly less balance than what it has promised to solvers/cancellers through the `_orders` mapping.

By contrast, the mainline EVM contract `evm/src/apps/IntentGatewayV2.sol` was hardened against exactly this scenario: it snapshots the balance before/after each `safeTransferFrom` and mutates `order.inputs[i].amount` to the *actually received* value before computing protocol fees and the commitment: [4](#0-3) 

The existence of this fix (and a dedicated `FeeOnTransferToken` test fixture in the EVM test suite) confirms the project explicitly recognizes and mitigates this bug class on the primary EVM deployment, but the Tron deployment was not updated with the same protection: [5](#0-4) 

### Impact Explanation
Because escrow bookkeeping (`_orders[commitment][token]`) can exceed the gateway's real token balance for a given input token, the contract becomes undercollateralized for that token. When solvers fill orders and later redeem escrow (via `RedeemEscrow`/fill flows) or users cancel orders for a refund, the aggregate amount the contract is obligated to pay out across all orders sharing that token can exceed what it actually holds. This allows an attacker to place an order with a fee-on-transfer token to inflate its own order's recorded escrow beyond the tokens it deposited, then have that order filled/cancelled to drain real tokens that were deposited by other, legitimate orders — a direct theft/insolvency vector against other users' escrowed funds. This is a fund-safety issue reachable from a single unprivileged `placeOrder` transaction.

### Likelihood Explanation
Likelihood depends on the Tron gateway ever being configured to accept a fee-on-transfer (or deflationary/rebasing-with-fee) token as an input asset. Given the project's own roadmap (as referenced in the original report) of adding more collateral/input tokens and deploying to additional chains, and given Tron's ecosystem includes TRC20 tokens with transfer-fee mechanics, this is a realistic configuration risk rather than a purely theoretical one — especially since the mainline EVM contract already had to be patched for this exact scenario, showing the team anticipated needing to support such tokens.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: measure `balanceOf(address(this))` (or the dispatcher, for the predispatch path) immediately before and after each `safeTransferFrom`/sweep, and use the actual delta as the amount fed into `reducedInputs`, the commitment hash, and `_orders[commitment][token]`, instead of trusting the caller-declared `order.inputs[i].amount`.

### Proof of Concept
1. Admin (or future governance) lists a fee-on-transfer TRC20 token as a valid input asset on the Tron `IntentGatewayV2`.
2. Attacker calls `placeOrder` declaring `inputs[0].amount = 1000` of the fee-on-transfer token (e.g., 5% fee). `safeTransferFrom` pulls 1000 from the attacker but the gateway's balance only increases by 950.
3. `reducedInputs[0].amount` is computed from the declared `1000` (minus protocol fee, if any), and `_orders[commitment][token] += reducedInputs[i].amount` credits close to 1000 tokens of escrow, while the contract's real balance for that token only grew by 950.
4. Repeating this (or combined with other users' legitimate deposits of the same token) causes the sum of all `_orders[...][token]` entries to exceed `IERC20(token).balanceOf(address(this))`.
5. When solvers fill orders / redeem escrow, the last redemptions for that token fail to be paid in full or, if fills are processed via internal accounting reductions rather than direct balance checks, an attacker-controlled order gets paid out using tokens that rightfully belong to another user's escrowed order, resulting in theft of those funds.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-446)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2689-2735)
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
        // fee is burned
        totalSupply -= fee;
        return true;
    }
}
```
