### Title
Fee-on-transfer token inputs in Tron `IntentGatewayV2.placeOrder` credit escrow with more than actually received, permanently freezing funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron fork of `IntentGatewayV2.placeOrder` does not account for fee-on-transfer (deflationary) input tokens in its direct-transfer path. It escrows the nominal `order.inputs[i].amount` (reduced only for protocol fee) instead of the amount actually received by the contract, unlike the audited/fixed EVM mainline contract which snapshots balances before/after transfer to capture the real received amount.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `placeOrder` first computes `reducedInputs` (protocol-fee-adjusted amounts) directly from the user-supplied `order.inputs[i].amount`, before any token transfer occurs: [1](#0-0) 

Then, in the non-predispatch branch, it performs `safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and immediately credits the escrow ledger `_orders[commitment][token]` with `reducedInputs[i].amount` — without ever checking the contract's actual token balance before/after the transfer: [2](#0-1) 

For a fee-on-transfer/deflationary ERC20 used as an input token, the contract will receive `order.inputs[i].amount - fee` tokens, but `_orders[commitment][token]` will be credited with the full (fee-reduced-only-by-protocol-fee) nominal amount. This is the same root cause identified in the referenced Teller `CollateralEscrowV1.depositAsset` report: the accounting ledger diverges from the actual token balance held in escrow.

This contrasts with the corrected logic present in the canonical EVM contract, which explicitly snapshots `balanceOf(address(this))` before and after `safeTransferFrom` and mutates `order.inputs[i].amount` to the actually-received delta before computing `reducedInputs` and crediting `_orders`: [3](#0-2) 

The predispatch branch of the Tron contract does correctly measure `balance` on the dispatcher before crediting dust vs. escrow (lines 416-446), but the primary/common direct-transfer path (lines 450-469) — used whenever `predispatch.call`/`predispatch.assets` are empty, i.e. the default and most common flow — has no such check.

### Impact Explanation
Any user placing an order with a fee-on-transfer token as input causes `_orders[commitment][token]` to record more tokens than the gateway actually holds for that commitment. Downstream:
- `_withdraw` in `IntentsBase.sol` reads the escrow ledger and calls `IERC20(token).safeTransfer(beneficiary, amount)` using the inflated recorded amount: [4](#0-3) 
  Since the contract's real balance of that token is lower than what is recorded, this transfer can fail (revert) when the ledger amount exceeds the actual balance, or — because token balances are fungible across all orders held by the same contract — succeeds by consuming balance that rightfully belongs to *other* users' escrowed orders, permanently freezing/breaking other legitimate withdrawals. Either outcome constitutes a permanent freezing of user or protocol funds, a High severity impact under the same reasoning as the original report (liquidation/withdraw reverting due to overstated escrow balances, or cross-order fund corruption).

### Likelihood Explanation
Any unprivileged user can trigger this in a single `placeOrder` transaction by specifying a fee-on-transfer/deflationary token as an input asset and taking the default (no-predispatch) code path, which is the normal, most-used flow. No special privileges, governance, or malicious actors are required — it is a direct consequence of using a standard (if non-vanilla) ERC20 token as collateral/input.

### Recommendation
In the non-predispatch branch of `placeOrder` (and any other direct-transfer paths), snapshot `IERC20(token).balanceOf(address(this))` before and after `safeTransferFrom`, and use the actual received delta (as done in `evm/src/apps/IntentGatewayV2.sol`) when computing `reducedInputs`/`_orders` credit, mutating `order.inputs[i].amount` to the received amount before the commitment hash and escrow bookkeeping are computed. This aligns the Tron contract with the fix already implemented in the canonical EVM `IntentGatewayV2.sol`.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` and a fee-on-transfer ERC20 (e.g., 1% fee on transfer, as modeled by the `FeeOnTransferToken` test helper used for the fixed EVM contract: [5](#0-4) ).
2. User approves and calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and no predispatch call/assets.
3. `safeTransferFrom` moves 1000e18 but the gateway actually receives only 990e18 (1% fee burned/retained by token).
4. `_orders[commitment][FOT]` is nonetheless credited with `reducedInputs[0].amount` derived from the full 1000e18 (minus only protocol fee, if any) — i.e. ~1000e18 rather than the true 990e18 balance.
5. When a solver later fills the order and the corresponding `_withdraw`/redeem path attempts `safeTransfer(beneficiary, escrowedAmount)` for the recorded (inflated) amount, the transfer either reverts (insufficient actual token balance) — freezing the order — or, if other orders hold balances of the same token, drains funds belonging to those other orders, corrupting their accounting and freezing their withdrawals.

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
