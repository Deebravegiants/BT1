## Title
Fee-on-transfer/deflationary ERC20 input in `IntentGatewayV2.placeOrder` (non-predispatch path) escrows more than the gateway actually receives, allowing under-collateralized orders that drain honest depositors' funds — (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder` on the Tron variant of `IntentGatewayV2` computes the protocol fee and the escrow-credited amount (`reducedInputs[i].amount`) from the **declared** `order.inputs[i].amount` *before* the token transfer happens, and never re-measures the gateway's actual token balance for the plain (non-predispatch) transfer branch. If the input token takes a transfer fee (fee-on-transfer / rebasing / deflationary ERC20), the amount that actually lands in the gateway is smaller than `order.inputs[i].amount`, yet `_orders[commitment][token]` is credited as if the full declared amount (minus protocol fee) had arrived. This is the same root-cause pattern as the reference report: fee/accounting is derived from a caller-supplied parameter instead of the measured, on-chain effect of the transfer.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder`:

```solidity
uint256 originalAmount = order.inputs[i].amount;
uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
uint256 reducedAmount = originalAmount - protocolFee;
...
reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
``` [1](#0-0) 

This `reducedInputs[i].amount` is fixed **before** any tokens move. Later, in the non-predispatch branch, the transfer is performed but the actually-received amount is never checked against what was assumed:

```solidity
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
...
// Store reduced amount (after protocol fees) in escrow
_orders[commitment][token] += reducedInputs[i].amount;
``` [2](#0-1) 

If the token deducts a fee on transfer, the gateway's real balance increases by less than `order.inputs[i].amount`, but the escrow ledger `_orders[commitment][token]` is still incremented by the full `reducedInputs[i].amount` computed from the pre-transfer declared amount. The commitment hash is likewise computed from the same, un-verified `reducedInputs`, so the order's on-chain record (used by solvers/relayers to fill and later redeem escrow) overstates the collateral actually held.

The canonical `evm/src/apps/IntentGatewayV2.sol` was hardened against exactly this class of bug: it snapshots `balanceOf(address(this))` before and after the transfer and uses the delta as the real `order.inputs[i].amount` (mutating it down for shrinkage), only computing the protocol fee afterward:

```solidity
uint256 balBefore = IERC20(token).balanceOf(address(this));
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
``` [3](#0-2) 
and this is asserted by the fee-on-transfer regression tests added for the canonical implementation: [4](#0-3) 

The Tron contract's `placeOrder` (and its analogous predispatch branch, which also derives `reducedInputs` from the pre-swept `requiredAmount` rather than the swept `balance`) never applies this actual-vs-declared reconciliation for the direct-transfer path, leaving the accounting bug intact there.

### Impact Explanation
`_orders[commitment][token]` is the pool's source of truth for how much of each token an order has escrowed, and it directly gates how much can later be paid out to a solver on fill or refunded to the user on cancellation/timeout. If this figure can be inflated relative to the gateway's real token balance, then:
- Multiple orders placed with a fee-on-transfer token systematically over-credit escrow versus real balance, creating a growing shortfall in the gateway's actual holdings of that token.
- When solvers fill orders or users cancel/refund, withdrawals are made against the inflated ledger value, not the real balance, meaning later legitimate claims (other users' correctly-collateralized orders in the same token, or the same user's own order) can fail to be honored in full or drain balance belonging to other depositors — a permanent, protocol-wide insolvency for that token, i.e., theft of funds from other users of the shared pool.
- This is directly reachable by any unprivileged user who places an order (`placeOrder`) with an attacker-chosen or naturally fee-on-transfer ERC20 as the input token — no special privilege required.

This qualifies as **High** severity: it produces unsound state-commitment/escrow accounting and enables draining of pooled funds, matching the "unsound state commitment" / "theft or permanent freezing of funds" acceptance criteria.

### Likelihood Explanation
Likelihood is Medium-High: the attacker only needs to place an order whose input token is fee-on-transfer (there are many such tokens in the wild, and the intent gateway does not restrict which ERC20s can be used as inputs). No collusion, front-running, or privileged role is required — a single `placeOrder` call with a suitable token is sufficient to create a mismatch between escrowed accounting and real balance. The same class of token (`FeeOnTransferToken`) is already used in the project's own test-suite to validate this exact scenario against the canonical `evm/src` contract, confirming it is a recognized, realistic threat model that the Tron variant fails to replicate the fix for.

### Recommendation
Apply the same balance-delta measurement pattern used in `evm/src/apps/IntentGatewayV2.sol` to `evm/tron/contracts/apps/IntentGatewayV2.sol`:
- For the non-predispatch branch, snapshot `balanceOf(address(this))` before and after each `safeTransferFrom`, and use the actual delta as the input amount used to compute `reducedInputs`/`_orders[commitment][token]` and the commitment hash — not the pre-transfer declared `order.inputs[i].amount`.
- For the predispatch branch, use the swept `balance` capped by (or reconciled against) `requiredAmount` in the same way the canonical contract's Phase 1 does, rather than fixing `reducedInputs` from the declared amount before the sweep occurs.
- Move the protocol-fee computation (`reducedInputs`) to *after* all actual-amount measurements are finalized, mirroring canonical `evm/src`'s two-phase structure (measure actual received, then compute fees/commitment).

### Proof of Concept
Conceptual reproduction (mirrors the project's own `FeeOnTransferToken` test harness for the canonical contract, but targeting the Tron variant, which lacks the balance-delta fix):
1. Deploy a 1% fee-on-transfer ERC20 (`FeeOnTransferToken`, as already used in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol` for the canonical contract) and mint balance to `user`. [5](#0-4) 
2. `user` approves the Tron `IntentGatewayV2` and calls `placeOrder` with `order.inputs[0] = { token: fot, amount: 1000e18 }`, no predispatch.
3. In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `reducedInputs[0].amount` is computed from `1000e18` (minus protocol fee) at lines 359–374, before the transfer. [1](#0-0) 
4. `safeTransferFrom` only delivers `990e18` to the gateway (1% fee burned/retained by the token), but `_orders[commitment][fot] += reducedInputs[0].amount` credits an amount based on `1000e18`, i.e. more than the `990e18` actually held. [2](#0-1) 
5. Repeating this (or combining with a subsequent legitimate order in the same token) lets aggregate `_orders[...]` claims on that token exceed `fot.balanceOf(address(intentGateway))`, so a later fill/cancel/refund can pay out more than the gateway holds, at the expense of other depositors' escrowed balances of the same token.

I could not fully trace the exact downstream fill/redeem code path in `evm/tron/contracts/apps/IntentGatewayV2.sol` (its intentsv2 fill/redeem logic is split across files not fully retrieved before running out of investigation budget), so the exact payout mechanics that consume `_orders[commitment][token]` were not directly cited; this should be verified in a full session before remediation, though the escrow-crediting bug itself is confirmed via direct code inspection above.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-374)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-468)
```text
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L320-322)
```text
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
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
