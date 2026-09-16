## Title
Fee-on-transfer tokens create insolvent escrow accounting in Tron `IntentGatewayV2.placeOrder` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits escrow with the user-requested input amount (minus protocol fee) instead of the amount actually received by the contract after `safeTransferFrom`. For fee-on-transfer ERC20 tokens, the gateway ends up under-collateralized: `_orders[commitment][token]` records more tokens than the contract actually holds.

### Finding Description
In the non-predispatch branch of `placeOrder`, tokens are pulled with `safeTransferFrom` but the actual received balance is never measured: [1](#0-0) 

The escrowed amount credited is `reducedInputs[i].amount`, which is derived directly from `order.inputs[i].amount` (the caller-specified amount) reduced only by the protocol fee — never by any transfer-fee deduction: [2](#0-1) 

For a fee-on-transfer token, `safeTransferFrom(msg.sender, address(this), amount)` delivers `amount - fee` to the gateway, yet `_orders[commitment][token]` is incremented by the full `reducedInputs[i].amount` (based on the requested `amount`), and the commitment hash is likewise computed from the pre-fee amount. This is exactly the bug class described in the external report: the contract assumes 1:1 delivery of ERC20 transfers when computing internal accounting.

This contrasts with the corresponding non-Tron EVM contract `evm/src/apps/IntentGatewayV2.sol`, which was explicitly hardened against this exact issue by measuring `balanceOf` before/after the transfer and mutating `order.inputs[i].amount` to the actual received amount before computing the commitment and crediting escrow: [3](#0-2) 

The Tron contract's `withdraw`/redemption path (`redeemEscrow`/`onGetResponse`) later pays out based on the escrowed bookkeeping value, not the real token balance: [4](#0-3) 

Since `_orders[commitment][token]` no longer reflects the tokens the gateway actually holds, the sum of all outstanding escrow entries for a fee-on-transfer token can exceed the gateway's real balance of that token.

### Impact Explanation
Once escrow bookkeeping for a fee-on-transfer token becomes inflated relative to the actual contract balance, the gateway becomes insolvent for that token:
- Earlier orders redeeming/withdrawing can drain the real balance, leaving later legitimate orders for the same token unable to be paid out — a permanent freezing of funds for those users/relayers (the raw `token.call(transfer(...))` succeeds only while balance suffices; once exhausted, subsequent withdrawals revert and the associated commitment can never be finalized).
- This also corrupts the commitment hash itself (computed with pre-fee amounts), meaning committed order data does not match what tokens the gateway custodies, breaking the invariant that escrow accounting mirrors custodied assets.

This is a protocol-level accounting break in the intents escrow reachable by any unprivileged user placing an order with a fee-on-transfer input token — it does not require any privileged role.

### Likelihood Explanation
Likelihood is moderate: it requires the deployment to whitelist/accept a fee-on-transfer ERC20 as a valid input token for orders on the Tron chain (many real-world stablecoins/tokens on Tron ecosystem, e.g., certain TRC20 tokens, implement transfer fees or are togglable like USDT). Given the codebase's own EVM Solidity file was patched specifically for this scenario (see fee-on-transfer tests in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`), the Tron contract clearly missed backporting that fix, making exploitation straightforward for any user who places an order using such a token — no special privileges or timing needed beyond normal order placement.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: measure the gateway's token balance before and after each `safeTransferFrom` call in `placeOrder` (both the predispatch-sweep and direct-transfer branches), mutate `order.inputs[i].amount` to the actual amount received, and only then compute the commitment hash and credit `_orders[commitment][token]`. Apply the equivalent fix to the Tron contract at `evm/tron/contracts/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with an ERC20 input token that charges e.g. a 1% fee on transfer.
2. User calls `placeOrder` with `order.inputs[0].amount = 1000e18`.
3. `safeTransferFrom(user, gateway, 1000e18)` executes; gateway actually receives `990e18` (fee-on-transfer deducts 1%).
4. `_orders[commitment][token]` is credited with `reducedInputs[0].amount` derived from `1000e18` (e.g. `1000e18` minus protocol fee), not the real `990e18` received — escrow bookkeeping now exceeds the gateway's real token balance by the transfer-fee amount.
5. Repeat with more orders for the same token: the aggregate escrowed balances recorded in `_orders` grow beyond the gateway's actual `balanceOf(gateway)`.
6. When orders are later filled/withdrawn via `withdraw(...)`, whichever redemption executes first successfully pays out at the (inflated) escrowed amount using real tokens; once the real balance is exhausted, later legitimate withdrawals for other valid orders on the same token revert, permanently freezing those funds.

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
