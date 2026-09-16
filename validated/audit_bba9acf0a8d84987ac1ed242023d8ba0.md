### Title
Fee-on-transfer tokens desync escrow accounting in Tron `IntentGatewayV2.placeOrder` - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits escrow (`_orders[commitment][token]`) based on the user-declared `order.inputs[i].amount` (reduced only by the protocol fee), while actually pulling funds via a plain `safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)`. Unlike the main EVM `evm/src/apps/IntentGatewayV2.sol`, which was patched to measure actual balance deltas before/after every transfer specifically to defend against fee-on-transfer tokens (see the `balBefore`/`balancesBefore` logic and inline comments about fee-on-transfer tokens), the Tron fork never re-adopted that fix, reintroducing the exact accounting bug described in the Velodrome `Bribe.sol` report.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the non-predispatch escrow path is:
```solidity
} else {
    for (uint256 i; i < inputsLen;) {
        if (order.inputs[i].amount == 0) revert InvalidInput();
        address token = address(uint160(uint256(order.inputs[i].token)));
        if (token == address(0)) {
            if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
            msgValue -= order.inputs[i].amount;
        } else {
            IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
        }
        // Store reduced amount (after protocol fees) in escrow
        _orders[commitment][token] += reducedInputs[i].amount;
        unchecked { ++i; }
    }
}
``` [1](#0-0) 

`reducedInputs[i].amount` is derived purely from `order.inputs[i].amount` minus a protocol-fee percentage — it is never adjusted for the actual tokens received: [2](#0-1) 

If `token` charges a transfer fee, the gateway contract's real balance increase is less than `order.inputs[i].amount`, yet `_orders[commitment][token]` is incremented by the (larger) declared/reduced amount. The predispatch branch has the same issue: dust is computed only against `order.inputs[i].amount`/`requiredAmount`, and `_orders[commitment][token] += reducedInputs[i].amount` still uses the undercorrected value: [3](#0-2) 

By contrast, the primary EVM contract explicitly fixes this exact class of bug by measuring `balanceOf` before and after every `safeTransferFrom`/sweep and mutating `order.inputs[i].amount` to the actual received value before computing the commitment and crediting escrow: [4](#0-3) [5](#0-4) 

The Tron file was never updated with this fix, so it silently over-credits escrow for any fee-on-transfer input token.

### Impact Explanation
This is the direct analog of the reported Velodrome `Bribe.sol` issue: the internal accounting ledger (`_orders[commitment][token]`, analogous to `tokenRewardsPerEpoch`) tracks more tokens than the contract actually holds. Because `IntentGatewayV2` pays out escrowed amounts to fillers/solvers on `RedeemEscrow`/fill flows based on this ledger value, the last filler(s) attempting to redeem an order funded with a fee-on-transfer token will be unable to receive their full recorded entitlement — the contract will not hold enough balance, causing reverts (denial of service / permanent freezing of that order's funds) or, in multi-order/multi-token settings, allowing the shortfall to be paid out of other orders' escrowed balances (fund misallocation among unrelated orders sharing the same token pool), which is a fund-safety break. This satisfies the "permanent freezing of funds" / "unsound state commitment" criteria for a Medium-severity issue, matching the original report's rating.

### Likelihood Explanation
Any unprivileged user can trigger this by calling `placeOrder` with an ERC20/TRC20 token that implements a transfer fee as one of the order's `inputs`. No special privileges are required — this is directly reachable from a single external `placeOrder` transaction, and the resulting inconsistency manifests automatically whenever the order is filled/redeemed. The only precondition is that a fee-on-transfer token is accepted as an input asset, which the contract does not explicitly disallow.

### Recommendation
Apply the same fix used in `evm/src/apps/IntentGatewayV2.sol` to the Tron variant: measure the gateway's (or dispatcher's) token balance immediately before and after each `safeTransferFrom`/sweep, and use the actual received delta — not the caller-declared `amount` — when computing `reducedInputs`, the commitment hash, and the `_orders[commitment][token]` escrow credit. Alternatively, maintain protocol-wide token allow-lists that exclude fee-on-transfer tokens for order inputs on the Tron deployment.

### Proof of Concept
1. Deploy a TRC20/ERC20 token with a transfer fee (e.g., 1%) on the Tron chain where `evm/tron/contracts/apps/IntentGatewayV2.sol` is deployed.
2. User approves and calls `placeOrder` with `inputs[0] = {token: feeToken, amount: 1000e18}` and no `protocolFeeBps` (or any value).
3. `safeTransferFrom` pulls 1000e18 from the user, but the gateway only receives 990e18 (1% fee) due to the token's fee-on-transfer mechanic.
4. `_orders[commitment][feeToken]` is nonetheless credited with `reducedInputs[0].amount` derived from the full 1000e18 (minus only protocol fee, if any) — i.e., more than the 990e18 actually held.
5. When a filler submits a `RedeemEscrow`/withdrawal request for this commitment expecting the full recorded escrow amount, the internal transfer (`safeTransfer`) will fail or partially drain other orders' balances because the gateway's actual token balance is insufficient to cover the recorded ledger value — reproducing the same "escrow ledger overstates actual holdings" failure mode as the referenced Velodrome `Bribe.sol` finding. [6](#0-5) [1](#0-0)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-385)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
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

**File:** evm/src/apps/IntentGatewayV2.sol (L363-373)
```text
        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

            unchecked {
                ++i;
            }
        }
```
