## Analysis

The Tron variant of `IntentGatewayV2.placeOrder()` reproduces exactly the "inconsistent modification of amount data" bug class from the Mover finding: the commitment (analogous to `_bridgeTxData`) is computed from a value that is **not** the actual amount transferred into escrow, whereas the escrow bookkeeping uses a *different* value than what commitment consumers (fillers/relayers) can independently verify against actual token flows.

### Title
Escrow credited with nominal `order.inputs[i].amount` while commitment/emitted amounts reflect protocol-fee-reduced values, causing fee-on-transfer and dust mismatches to permanently strand funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
In `placeOrder()` of the Tron `IntentGatewayV2`, the protocol-fee-reduced `reducedInputs` and the `commitment` hash are computed **before** tokens are actually pulled from the user [1](#0-0) , using the nominal `order.inputs[i].amount` supplied by the caller rather than the amount actually received by the contract. The subsequent transfer-in step (`safeTransferFrom`) does not re-derive `reducedInputs` from the real received balance for the non-predispatch path [2](#0-1) , unlike the mainline EVM `IntentGatewayV2.sol`, which explicitly computes actual received amounts first (via balance-diff checks) and only then derives `reducedInputs`/`commitment` from those real amounts [3](#0-2) .

### Finding Description
The correct/mainline pattern (`evm/src/apps/IntentGatewayV2.sol`) is: Phase 1 transfers tokens and records the *actual* received amount via balance-before/after diffing (handles fee-on-transfer tokens, dust) [4](#0-3) ; Phase 2 computes protocol fees and the commitment strictly from these actual received amounts [5](#0-4) .

The Tron variant inverts this ordering: it computes `reducedInputs` and `commitment` from `order.inputs[i].amount` — the amount the *caller declared*, not what is actually received — before any transfer happens [1](#0-0) . Then, in the non-predispatch escrow path, it calls `safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` without checking the actual balance received, and unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount` [6](#0-5) .

This is the direct analog of the Mover `_bridgeTxData` bug: one code path (predispatch, lines 416–446) does re-derive amounts from actual balances (`balance`, `dust`) before crediting escrow [7](#0-6) , while the other path (non-predispatch, the common case) blindly trusts the nominal, pre-fee-deduction amount and never verifies actual receipt, exactly mirroring the "consistent for one code path, inconsistent for the other" defect pattern flagged in the original report.

For any fee-on-transfer ERC20 token used as an order input (deflationary/tax tokens), or any token where `transferFrom` can deliver less than requested, the gateway will:
1. Credit `_orders[commitment][token]` with `reducedInputs[i].amount` computed from the *nominal* `order.inputs[i].amount`, which is strictly greater than what was actually received.
2. Never detect the shortfall, since there's no balance-before/after check in this path (unlike the predispatch branch and unlike the mainline EVM contract).

### Impact Explanation
This creates an escrow accounting entry (`_orders[commitment][token]`) that overstates the gateway's actual token balance for that order. When a solver later calls `fillOrder`/redeems the escrow (via `RedeemEscrow`/withdraw flows), the contract will attempt to pay out more than it physically holds for that specific token bucket, either reverting the fill/redemption for that order (permanent freeze of the honest solver's expected settlement and the user's overstated escrow) or, if the shared token pool across orders happens to have slack from other orders' fee-on-transfer overpayments, silently draining tokens that belong to other users' escrowed orders — an insolvency/fund-drain condition. Both outcomes (frozen orders / cross-order fund misappropriation) meet the Medium+ bar for "concrete theft or permanent freezing of funds."

### Likelihood Explanation
Reachable by any unprivileged user submitting a single `placeOrder()` transaction with a fee-on-transfer or non-standard ERC20 as `order.inputs[i].token` on the Tron deployment — no special privileges required. The predispatch branch already contains the correct fix pattern in the same file, confirming this is an inconsistency (missed application of the same defensive logic to the more commonly used non-predispatch path) rather than a deliberate design choice.

### Recommendation
Mirror the mainline EVM `IntentGatewayV2.sol` ordering in the Tron variant: in the non-predispatch branch, capture `balanceBefore`/`balanceAfter` around each `safeTransferFrom` to compute the actual received amount per input, and use these actual received amounts (not `order.inputs[i].amount`) as the basis for computing `reducedInputs`, the `commitment`, and the value credited to `_orders[commitment][token]`, consistent with `evm/src/apps/IntentGatewayV2.sol` lines 312–361.

### Proof of Concept
1. Deploy Tron `IntentGatewayV2` with `protocolFeeBps > 0`.
2. User calls `placeOrder()` with `order.inputs[0]` set to a fee-on-transfer token address and `amount = 1000` (no predispatch call/assets).
3. Contract computes `reducedInputs[0].amount = 1000 - protocolFee` and `commitment = keccak256(abi.encode(order))` using the nominal `1000` [1](#0-0) .
4. `safeTransferFrom(msg.sender, address(this), 1000)` is called, but the fee-on-transfer token only delivers e.g. `950` to the gateway (5% transfer tax) [8](#0-7) .
5. `_orders[commitment][token] += reducedInputs[0].amount` credits the escrow with `1000 - protocolFee` (e.g., ~995), while the gateway's actual token balance for that token only increased by `950` [9](#0-8) .
6. When the order is later filled/redeemed for `995` tokens, the contract attempts to pay out more than it received for this order, causing either a revert (frozen settlement) or depletion of other users' escrowed balances of the same token if aggregate liquidity permits the transfer to succeed.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L417-441)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L312-361)
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
