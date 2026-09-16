### Title
Unvalidated fee-on-transfer/deflationary token accounting lets escrow credit exceed actual tokens held, enabling insolvency in `placeOrder` - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder` on the Tron variant credits the escrow mapping `_orders[commitment][token]` with the *requested* input amount (minus protocol fee) without ever measuring the tokens actually received by the contract. This mirrors the Blueberry `_repay()` bug class: an unvalidated "expected vs. actual" amount is fed directly into a balance/share accounting update, allowing the on-chain bookkeeping to diverge from real token custody.

### Finding Description
In `placeOrder` (evm/tron/contracts/apps/IntentGatewayV2.sol), the non-predispatch escrow path does: [1](#0-0) 

It calls `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount`, where `reducedInputs[i].amount` is derived purely from `order.inputs[i].amount` (the user-declared/requested amount) minus the protocol fee: [2](#0-1) 

No balance-before/after check is performed to confirm the contract actually received `order.inputs[i].amount` of the token. This is the "paid vs amountCall" gap from the Blueberry report: the accounting trusts a value (`order.inputs[i].amount`) that can legitimately diverge from the actual transferred amount for any fee-on-transfer, rebasing, or otherwise deflationary ERC-20, yet uses it unchecked to update the internal escrow ledger that later determines real token payouts.

By contrast, the primary EVM contract at `evm/src/apps/IntentGatewayV2.sol` was hardened against exactly this: it snapshots balances before and after each transfer and mutates `order.inputs[i].amount` to the actual received amount before computing `reducedInputs` and crediting escrow: [3](#0-2) [4](#0-3) 

The predispatch path in the Tron contract computes a `dust` value from `balance - requiredAmount` (correctly guarded), but crucially, that measured `balance` is *not* what gets credited to escrow — the code still credits the pre-computed `reducedInputs[i].amount` (based on the declared amount), not the observed balance: [5](#0-4) 

When the order is later filled/redeemed, `withdraw()` pays out exactly the escrow-book amount via a direct `IERC20.transfer`, without any re-check against the contract's actual token balance: [6](#0-5) 

### Impact Explanation
If a user places an order using a deflationary/fee-on-transfer token as input, the gateway records (and later pays out to solvers/relayers) an escrow amount greater than what it actually holds for that commitment. Because escrow accounting is a global ledger shared across all outstanding orders/commitments in the same token, an inflated book entry for one order can only be honored by draining tokens that legitimately back other users' escrowed orders — a direct insolvency/fund-freezing vector reachable by any unprivileged caller of `placeOrder` with a single transaction, requiring no admin, governance, or special privilege. This satisfies "concrete theft or permanent freezing of funds" from unbacked internal accounting.

### Likelihood Explanation
High: `placeOrder` is a fully permissionless, single-transaction entry point. The only precondition is providing a token address with any transfer-fee/rebase/deflationary behavior as `order.inputs[i].token` — attacker fully controls token choice via `order.inputs`, and no allowlist appears to restrict input tokens in this function. This requires no collusion, no privileged role, and no complex multi-step exploit.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: snapshot the contract's (or dispatcher's) token balance immediately before and after each `safeTransferFrom`/predispatch sweep, and use the *actual delta* (not the declared `order.inputs[i].amount`) as the basis for `reducedInputs`, the commitment hash, and the `_orders[commitment][token]` credit in the Tron variant of `IntentGatewayV2.sol`.

### Proof of Concept
1. Attacker deploys or picks an existing fee-on-transfer ERC-20 token `FOT` (1% fee on transfer), analogous to the test fixture already used in this codebase's own test suite: [7](#0-6) 
2. Attacker calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs[0] = {token: FOT, amount: 1000e18}`.
3. `safeTransferFrom` moves `1000e18` from attacker but the gateway only receives `990e18` (1% fee burned/kept by token).
4. `reducedInputs[0].amount` is computed from the declared `1000e18` (minus any protocol fee), not the `990e18` actually received, and `_orders[commitment][FOT] += reducedInputs[0].amount` credits more than the gateway holds.
5. When the order is later filled and `withdraw()` is invoked, it attempts to `IERC20(FOT).transfer(beneficiary, amount)` for the inflated `amount`, which either reverts (freezing legitimate withdrawal, DoS on this order/token) or succeeds by consuming FOT balance escrowed by other unrelated orders in the same token, breaking their backing and enabling theft/insolvency across the ledger.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-468)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
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

**File:** evm/src/apps/IntentGatewayV2.sol (L340-368)
```text
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

        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;
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
