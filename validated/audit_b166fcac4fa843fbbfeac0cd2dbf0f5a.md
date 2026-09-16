### Title
Missing balance check on fee-on-transfer input tokens in `placeOrder` causes escrow accounting to overstate actual holdings - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the `placeOrder` function's non-predispatch escrow path pulls ERC-20 input tokens via `safeTransferFrom` and credits the internal `_orders` escrow ledger using the *requested* `order.inputs[i].amount` (minus protocol fee), without verifying the amount actually received by the contract. If the input token charges a fee-on-transfer (or otherwise delivers less than the nominal amount), the escrow ledger will record more tokens than the contract actually holds.

### Finding Description
`placeOrder` computes `reducedInputs[i].amount` from `order.inputs[i].amount` (the nominal, user-specified amount) and increments `_orders[commitment][token] += reducedInputs[i].amount` after simply calling: [1](#0-0) 

No balance-before/after check is performed for the ERC-20 branch, unlike the native-token branch which checks `msgValue` explicitly. This is the exact analog of the reported bug class: transferred amount is assumed instead of measured.

Notably, the sibling non-Tron implementation (`evm/src/apps/IntentGatewayV2.sol`) has already been hardened for this exact issue: it snapshots `balanceOf` before and after each `safeTransferFrom`/sweep and uses `IERC20(token).balanceOf(address(this)) - balBefore` as the actual received amount before crediting escrow: [2](#0-1) [3](#0-2) 

The Tron variant's `placeOrder` predispatch branch also does the safer `balanceOf`-based dust-checking: [4](#0-3) 
but the direct-escrow (non-predispatch) branch at lines 450-468 was not updated to match, leaving it vulnerable.

### Impact Explanation
When a fee-on-transfer (or any deflationary/rebasing-down) ERC-20 is used as an order input, `_orders[commitment][token]` will be credited for more tokens than the gateway contract actually holds. Later, when the order is filled and `withdraw` (which trusts the `_orders` mapping) releases the escrowed amount to the beneficiary/solver via `transfer`/`safeTransfer`: [5](#0-4) 
the contract can end up paying out more of that token than it actually received from this specific order, which is settled from the shared token balance of the contract — draining balance backing other users' unrelated escrowed orders of the same token. This is a fund-freezing/insolvency vector: honest users placing orders in other tokens or the same token can be left unable to redeem their escrow because the pooled balance has been depleted by the shortfall, and it can also be leveraged by an attacker to intentionally place orders with a known fee-on-transfer token to siphon value from the shared escrow pool.

### Likelihood Explanation
Likelihood depends on protocol/governance allow-listing which ERC-20s can be used as order inputs; if any fee-on-transfer, rebasing, or otherwise non-standard ERC-20 is permitted as an input asset (there is no on-chain restriction against it in `placeOrder`), any unprivileged user calling `placeOrder` triggers the discrepancy deterministically on every such order. This is a single-transaction, unprivileged, directly reachable code path (`placeOrder` is the intent-creation entry point), matching the in-scope "intents escrow" class.

### Recommendation
Apply the same balance-snapshot pattern already used in `evm/src/apps/IntentGatewayV2.sol` and in the Tron file's own predispatch branch to the non-predispatch ERC-20 branch of `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder`: record `balanceOf(address(this))` before `safeTransferFrom`, and after the transfer set `order.inputs[i].amount` (and consequently `reducedInputs[i].amount`/escrow credit) to the actual balance delta rather than the nominal requested amount.

### Proof of Concept
1. Governance/params allow a fee-on-transfer ERC-20 token `T` (e.g., 1% transfer fee) as a valid input asset (no code prevents this).
2. User A calls `placeOrder` with `order.inputs = [{token: T, amount: 1000}]` and no predispatch call.
3. `IERC20(T).safeTransferFrom(msg.sender, address(this), 1000)` executes, but due to the 1% fee, the contract only receives 990 `T`. [6](#0-5) 
4. `_orders[commitment][T] += reducedInputs[0].amount`, where `reducedInputs[0].amount` is derived from the nominal `1000` (minus protocol fee), not the actual `990` received — the ledger overstates the true balance held for this order by ~10 tokens.
5. When another user B's separate order (also denominated in `T`) is later filled/cancelled and `withdraw` executes `transfer`/`safeTransfer` for the recorded escrow amount, the pooled `T` balance in the contract is insufficient to cover all recorded escrow entries, causing either a revert (freezing B's funds) or, in the presence of enough legitimate excess balance from other operations, a payout that silently drains balance backing unrelated orders.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-700)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L260-311)
```text
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
