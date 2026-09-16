### Title
Tron `IntentGatewayV2.placeOrder` credits escrow with the declared input amount instead of the actual received balance, letting locked escrow diverge from real token holdings for non-standard ERC-20s - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The mainline EVM `IntentGatewayV2.sol` was hardened so that `placeOrder` measures the gateway's *actual* token balance delta after each `transferFrom` and uses that measured amount for both the commitment hash and the escrow ledger (`_orders`), specifically to protect against fee-on-transfer / deflationary tokens where declared amount ≠ received amount [1](#0-0) . The Tron variant of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, still uses the old, unhardened logic: it pulls `order.inputs[i].amount` (msg.sender's declared amount) via `safeTransferFrom`, but credits the escrow accounting map `_orders[commitment][token]` with `reducedInputs[i].amount`, which is derived from the *declared* amount minus the protocol fee, not from any measured balance delta [2](#0-1) . This is structurally the same class of bug as the Lyra report: an internal accounting variable (`lockedCollateral.base` / here `_orders[commitment][token]`) is incremented unconditionally while the actual backing balance (sETH balance / here the gateway's real token balance) can silently diverge from it.

### Finding Description
In `placeOrder` (non-predispatch path), the Tron contract does:
```solidity
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
// Store reduced amount (after protocol fees) in escrow
_orders[commitment][token] += reducedInputs[i].amount;
``` [3](#0-2) 

`reducedInputs[i].amount` is computed purely from `order.inputs[i].amount * (1 - protocolFeeBps)` — it is never reconciled against what the gateway actually received [4](#0-3) . For any ERC-20 with a transfer fee, rebase, or any deviation between "amount specified" and "amount received" (common on Tron, e.g. certain TRC-20 wrappers), the gateway's real token balance ends up lower than the sum of `_orders[commitment][token]` entries it believes it is holding. The predispatch branch of the same file has an identical pattern: it computes `dust = balance - requiredAmount` for events only, but still credits `_orders[commitment][token] += reducedInputs[i].amount` unconditionally, rather than crediting the actually-swept balance [5](#0-4) .

This is the direct root cause matching the reported bug class: the gateway maintains an escrow accounting ledger that is not capped by / reconciled to the real token balance it custodies. By contrast, the already-remediated mainline `IntentGatewayV2.sol` fixed this exact issue by measuring `balanceOf` before and after every transfer and using the measured delta as `order.inputs[i].amount` before fee reduction and escrow crediting [6](#0-5) , and its Foundry test suite specifically asserts "Escrow should equal actual received amount" for fee-on-transfer tokens [7](#0-6) . The Tron deployment was not given the equivalent fix.

### Impact Explanation
Because escrow accounting is per-`commitment`-per-`token` and multiple orders share the same pooled gateway balance, one under-collateralized order (escrow entry > actual tokens deposited for it) does not fail immediately — it is masked by surplus balance from other orders' honest deposits, exactly as the original report describes ("liquidity pool can run out of sUSD," affecting withdrawals/settlements). Over time, as multiple orders using a fee-charging or otherwise short-transferring token are placed, cancelled, or redeemed, the sum of `_orders[...]` escrow liabilities can exceed the gateway's real token balance. When solvers fill orders and the protocol later attempts to release/redeem the full recorded escrow (via `RedeemEscrow`/`_withdraw` cross-chain flows or same-chain cancellation refunds), a legitimate withdrawal for one order can revert due to insufficient real balance, or worse, drain balance intended for other users' escrow, i.e., permanent freezing or shortfall of user/solver funds. This is a Medium/High severity fund-safety issue reachable directly from a single unprivileged `placeOrder` transaction.

### Likelihood Explanation
Likelihood is contingent on the target token behaving as fee-on-transfer/deflationary or otherwise short-transferring on Tron/TRC-20 style tokens deployed via this gateway — a condition the mainline codebase explicitly anticipated and tested for (see the extensive `FeeOnTransferToken` test suite) [8](#0-7) , confirming this is a realistic, non-hypothetical token class the protocol must support/guard against. Since the Tron contract accepts arbitrary `TokenInfo.token` addresses supplied by any user in `placeOrder`, any unprivileged caller can trigger the mismatch with a single transaction using such a token, with no special privileges required.

### Recommendation
Mirror the mainline fix in `evm/tron/contracts/apps/IntentGatewayV2.sol`: measure `IERC20.balanceOf(address(this))` before and after each `safeTransferFrom` (and after the predispatch sweep) and use the measured delta as the input amount fed into protocol-fee computation, commitment hashing, and `_orders[commitment][token]` crediting, exactly as done in `evm/src/apps/IntentGatewayV2.sol:312-330`. This guarantees the escrow ledger is always capped by (equal to) the token balance actually custodied for that order, eliminating the ability for accounting to diverge from real holdings.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` with `protocolFeeBps = 0` for simplicity.
2. Deploy a fee-on-transfer ERC-20/TRC-20 token (1% fee), mint to `user`.
3. `user` calls `placeOrder` with `inputs[0].amount = 1000` of the fee token; `user` approves 1000.
4. Inside `placeOrder`, `safeTransferFrom(user, gateway, 1000)` executes, but due to the 1% fee the gateway's real balance only increases by 990.
5. Because `protocolFeeBps == 0`, `reducedInputs = order.inputs` (still `1000`), so `_orders[commitment][token] += 1000` — the escrow ledger records 1000 while the gateway physically holds 990.
6. Any subsequent full redemption/refund attempting to pay out the recorded `1000` from real balance will either revert (denial of service on withdrawal) or, if pooled with other orders' balances, silently consume other users' escrowed funds — reproducing the "differences between locked accounting and real balance are not capped" condition from the original report.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L312-330)
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2476-2493)
```text
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
