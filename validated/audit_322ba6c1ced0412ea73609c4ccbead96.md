### Title
Fee-on-transfer tokens cause escrow/balance mismatch in Tron `IntentGatewayV2.placeOrder` leading to stuck/unredeemable funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits escrow (`_orders[commitment][token]`) using the user-requested/reduced input amount rather than the actual token amount the contract received via `safeTransferFrom`. For fee-on-transfer (or otherwise deflationary) ERC-20 tokens, the actual balance held by the gateway will be lower than the amount recorded in escrow, causing later redemption/fill/cancel flows to attempt transferring more tokens than the contract actually holds.

### Finding Description
In the non-predispatch branch of `placeOrder`, tokens are pulled with a plain `safeTransferFrom` call and the escrow map is incremented by the pre-fee `reducedInputs[i].amount`, with no balance-before/after check: [1](#0-0) 

The predispatch branch has the same defect — it computes `dust` from the dispatcher-side balance snapshot but still credits escrow with the pre-transfer `reducedInputs[i].amount` instead of what the gateway itself actually received after the final sweep transfer: [2](#0-1) 

This is the exact same root cause described in the external report for `Allo.sol` — crediting an internal accounting variable with the pre-fee amount instead of the actually-received (post-fee) amount, when the underlying ERC-20 can take a cut on transfer.

Contrast this with the fixed EVM mainline version of the same contract, `evm/src/apps/IntentGatewayV2.sol`, which explicitly snapshots `balanceOf` before and after each transfer and mutates `order.inputs[i].amount` to the actually-received amount before computing the commitment/escrow, exactly to defend against this bug class: [3](#0-2) 

The Tron copy of the contract (`evm/tron/contracts/apps/IntentGatewayV2.sol`) was not updated with this fix and remains vulnerable.

### Impact Explanation
Because `_orders[commitment][token]` (the escrow ledger used by `fillOrder`, `cancelOrder`, and cross-chain `RedeemEscrow` handling) is inflated relative to the gateway's actual token balance, any downstream code path that transfers out `_orders[commitment][token]` (e.g. paying the solver on `fillOrder`, refunding the user on cancel, or fulfilling a `RedeemEscrow` withdrawal request) will attempt to send more tokens than the contract holds. This reverts for the affected order, and — more importantly — because escrow accounting is shared per `token` across the pool of all outstanding orders, the shortfall can also cause other, unrelated orders using the same token to be unable to fully settle once the contract's real balance is depleted by earlier claims (first-claimers succeed, later legitimate claimants fail), i.e., a permanent freezing-of-funds condition for at least one order's user or solver. This qualifies as Medium/High severity: concrete freezing of user/solver funds reachable from a single `placeOrder` transaction with any fee-on-transfer ERC-20 configured as an intent input token.

### Likelihood Explanation
Likelihood depends on whether Hyperbridge/IntentGateway permits arbitrary/permissionless ERC-20 tokens as order inputs on the Tron deployment. Tron's TRC-20 ecosystem commonly includes deflationary/tax tokens, and nothing in `placeOrder` restricts `order.inputs[i].token` to an allowlist of "safe" tokens — any user can specify any TRC-20 address as input. Given the project's own EVM mainline codebase already added fee-on-transfer handling and dedicated tests (`testPlaceOrder_FeeOnTransferToken_*` in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`) acknowledging this exact risk, the omission of the same fix in the Tron contract represents a real, currently reachable gap rather than a theoretical one.

### Recommendation
Apply the same fix used in `evm/src/apps/IntentGatewayV2.sol` to `evm/tron/contracts/apps/IntentGatewayV2.sol`: measure `balanceOf(address(this))` (or the relevant holder) before and after each `safeTransferFrom`/sweep, and use the actually-received delta — not the requested/reduced amount — both when computing the commitment hash and when incrementing `_orders[commitment][token]`.

### Proof of Concept
1. Deploy a fee-on-transfer TRC-20 token with, e.g., a 5% transfer fee (mirroring the `FeeOnTransferToken` test contract already present in the mainline test suite: [4](#0-3) ).
2. Call `IntentGatewayV2.placeOrder` on the Tron contract with `order.inputs[0]` = 1000 units of the fee token. `safeTransferFrom` in [5](#0-4)  pulls 1000 units nominally but the gateway only receives 950 due to the 5% fee.
3. Escrow is nonetheless credited with `reducedInputs[i].amount` (≈1000, or 1000 minus protocol fee) at [6](#0-5) , while `IERC20(token).balanceOf(address(this))` is only 950.
4. When a solver later fills the order or the user cancels, the contract attempts to pay out the escrowed (inflated) amount, which exceeds the actual token balance held, causing that transfer to revert (denial of settlement) or, if other orders share the same token pool, silently draining balance intended for other unrelated escrowed orders — leaving some order's beneficiary permanently unable to claim their funds.

### Citations

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2690-2734)
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
```
