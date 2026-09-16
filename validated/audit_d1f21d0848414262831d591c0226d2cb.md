Confirmed: `_withdraw` in `IntentsBase.sol` pays out based purely on the `_orders[commitment][token]` escrow accounting, decrementing it and doing a plain `safeTransfer`/`_sendValue` — it never re-checks actual contract balance against outstanding escrow across all commitments [1](#0-0) . This makes the correctness of `_orders` accounting depend entirely on `placeOrder` crediting escrow with the amount actually received by the contract.

### Title
Fee-on-transfer / deflationary tokens cause escrow insolvency in the Tron `IntentGatewayV2.placeOrder` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron fork of `IntentGatewayV2.placeOrder` credits the `_orders[commitment][token]` escrow mapping using the amount the user *requested* to deposit (`order.inputs[i].amount`, or a `reducedInputs[i].amount` derived from it), not the amount the contract actually receives from `safeTransferFrom`. For fee-on-transfer/deflationary ERC-20 tokens, this creates an escrow entry larger than the tokens actually held, breaking the invariant that `_withdraw` (shared across all orders/tokens) relies on.

### Finding Description
In the mainline EVM `IntentGatewayV2.sol`, `placeOrder` was specifically hardened against fee-on-transfer tokens: it measures the contract's token balance before and after `safeTransferFrom`, mutates `order.inputs[i].amount` to the *actual received* amount, and only then computes the commitment hash and protocol-fee-reduced escrow amounts from that real, received value [2](#0-1) [3](#0-2) . There is even a dedicated Foundry test validating this behavior [4](#0-3)  using a purpose-built `FeeOnTransferToken` mock [5](#0-4) .

However, the Tron variant of the contract (`evm/tron/contracts/apps/IntentGatewayV2.sol`) computes `reducedInputs`/`commitment` from `order.inputs[i].amount` (the caller-supplied, pre-transfer amount) *before* any token transfer happens, and then transfers via a plain `safeTransferFrom` without measuring the actual balance received [6](#0-5) [7](#0-6) . It then credits `_orders[commitment][token] += reducedInputs[i].amount` using that pre-transfer figure [8](#0-7) .

If `token` charges a transfer fee (deflationary/fee-on-transfer token), the gateway's actual balance increase is strictly less than the amount credited to escrow. Since `_orders` is a single global mapping shared by all orders that use the same token, and `_withdraw` blindly decrements this mapping and transfers out the recorded amount with no balance-sufficiency check [9](#0-8) , the over-credited escrow entries create a shortfall: eventually a legitimate solver/user calling `fillOrder`/`cancelOrder` for that token will find the contract's actual token balance insufficient to honor the escrow ledger, and the `safeTransfer` call reverts, or (if partial repeated fills draw down the shared pool) an earlier order can drain balance that rightfully belongs to a later, unrelated order using the same token — a fund-freezing/insolvency condition for other users' escrowed tokens.

The predispatch branch of the same function has an analogous problem: dust is computed from the dispatcher's balance *before* the final sweep transfer to `address(this)`, which itself may be subject to another transfer fee, so the actually-received amount at the gateway is again not what's credited to escrow [10](#0-9) .

### Impact Explanation
This is a direct analog of the "inflation/deflation tokens" bug class: any whitelisted, fee-on-transfer ERC20 token routed through the Tron `IntentGatewayV2` causes the escrow ledger to diverge from the real token balance held by the contract. Because `_orders` is a shared per-token accounting structure across all commitments, and withdrawal never validates against actual balance, this results in permanent freezing of funds for some order(s) sharing that token (their withdrawal reverts due to insufficient balance) or effectively insolvency where later legitimate withdrawals cannot be honored — a Medium-severity fund-freezing/accounting-insolvency issue reachable directly from an unprivileged user's single `placeOrder` transaction.

### Likelihood Explanation
Likelihood depends on whether fee-on-transfer/deflationary tokens are permitted as intent inputs on the Tron deployment. Since the codebase's own fix (balance-diff measurement) and dedicated tests in the mainline EVM contract show this token class is expected to be supported/whitelisted by the protocol, and the Tron contract is a near-duplicate that omits the fix, this is realistically triggerable whenever such a token is listed for intents on Tron.

### Recommendation
Port the balance-diff based fix from `evm/src/apps/IntentGatewayV2.sol` to `evm/tron/contracts/apps/IntentGatewayV2.sol`: measure `IERC20(token).balanceOf(address(this))` before and after each `safeTransferFrom`, mutate the recorded input amount to the actual received delta, and compute the commitment hash and `reducedInputs`/escrow credit from that actual-received amount rather than the caller-supplied `order.inputs[i].amount`. Apply the same balance-diff discipline to the predispatch sweep path.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g., 1% fee) and whitelist it as an intent input token on the Tron `IntentGatewayV2`.
2. User A calls `placeOrder` with `inputs[0].amount = 1000` of this token; the contract computes `commitment` and credits `_orders[commitment][token] = 1000` (assuming no protocol fee) via `_orders[commitment][token] += reducedInputs[i].amount` [8](#0-7) , but the contract's actual token balance only increased by 990 due to the transfer fee.
3. User B places a second order with the same token, also crediting escrow for the full requested amount while only actually receiving the fee-reduced amount.
4. As orders are filled/cancelled via `_withdraw`, the aggregate escrow claims recorded in `_orders` exceed the contract's real token balance by the accumulated transfer-fee shortfall; a later `_withdraw` call's `safeTransfer` for the correct escrowed amount reverts because the token balance is insufficient [11](#0-10) , freezing that user's/solver's funds.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
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

**File:** evm/src/apps/IntentGatewayV2.sol (L331-361)
```text
        // Phase 2: Compute protocol fees and commitment from actual received amounts.
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                if (originalAmount == 0) revert InvalidInput();
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            order.inputs = reducedInputs;
        } else {
            reducedInputs = order.inputs;
        }
        commitment = keccak256(abi.encode(order));
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2496-2515)
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L356-385)
```text
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

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
