### Title
Malicious/fee-on-transfer input token can desynchronize escrow accounting via balanceOf-diff crediting in `placeOrder` - (File: evm/src/apps/intentsv2/ExtrinsicIntents.sol / evm/src/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder` credits the escrow ledger `_orders[commitment][token]` using a "balance-before/balance-after" delta computed from `IERC20(token).balanceOf(address(this))` around `safeTransferFrom`, exactly the pattern flagged as exploitable in the reported `MainVault.deposit` analog. Because `order.inputs[i].token` is a user-supplied, unvalidated address, a user can place an order with a token contract they fully control and whose `balanceOf` return value they can manipulate across calls, causing the gateway to credit an escrow amount that does not correspond to real value actually held by the contract.

### Finding Description
In the non-predispatch branch of `placeOrder`:
```solidity
uint256 balBefore = IERC20(token).balanceOf(address(this));
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
``` [1](#0-0) 

and the predispatch/sweep branch:
```solidity
uint256 balance = IERC20(token).balanceOf(dispatcher);
...
balancesBefore[i] = IERC20(token).balanceOf(address(this));
...
received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
...
order.inputs[i].amount = received;
``` [2](#0-1) 

The resulting `order.inputs[i].amount` (after optional protocol-fee reduction) is written directly into escrow:
```solidity
reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
...
_orders[commitment][token] = reducedInputs[i].amount;
``` [3](#0-2) 

`order.inputs[i].token` is fully attacker-controlled (any address cast from `bytes32`), with no allow-list check anywhere in `placeOrder`. `balanceOf` is a `view`/non-restricted external call whose return value the token contract's author fully controls; a malicious ERC-20 can return an inflated "after" balance on the second call within the same transaction (e.g., stateful logic keyed on call count, `tx.origin`, or a flag toggled inside `transferFrom`) without the gateway ever actually holding that much real value. This lets `order.inputs[i].amount` — and hence `_orders[commitment][token]` — be set arbitrarily higher than what was truly escrowed.

### Impact Explanation
Once the escrow ledger for a fake/malicious token is inflated, a solver who fills the order via `_fillSameChain`/`_withdraw` is told (via `OrderPlaced`/order data) that `escrowedAmount` in the malicious token is available and releases it to itself (`IERC20(token).safeTransfer(beneficiary, amount)` in `_withdraw`) in exchange for real output tokens sent to the beneficiary:
```solidity
_orders[body.commitment][token] = escrowed - amount;
...
IERC20(token).safeTransfer(beneficiary, amount);
``` [4](#0-3) 

Because the "escrowed" token is one the attacker deployed and controls, `safeTransfer` can be made to succeed while conveying no real economic value (e.g., the token's `transfer` function is a no-op or reverts are avoided, or the token is worthless/mintable). The solver, having paid genuine output assets (the desired token specified in `order.output`) to the beneficiary, receives back a worthless/fabricated "input" token. This is a direct theft-of-funds vector against solvers/relayers filling orders, i.e. unbacked value is introduced into the escrow accounting, matching the reported bug class (balance manipulation via a second `balanceOf`/`getVaultBalance` call producing a false delta and false credited shares/amount).

### Likelihood Explanation
Likelihood is high for any order whose `order.inputs[i].token` is an attacker-deployed contract: nothing in `placeOrder`, `_fillSameChain`, or `_withdraw` validates that the input token is a well-known/trusted asset, nor re-verifies that `_orders[commitment][token]` corresponds to real token balance held by the gateway at time of release. The attack requires only a single `placeOrder` transaction using a custom ERC-20 whose `balanceOf` lies, and a counterparty solver willing to fill the order (which the attacker can arrange themselves as their own solver, or by publishing an attractive fill opportunity to lure a real solver).

### Recommendation
Mirror the reporter's fix for `MainVault.deposit`: after crediting escrow from a computed balance delta, do not trust a second `balanceOf` call blindly for security-critical accounting on arbitrary tokens. Concretely:
- Maintain an internal running total of tokens the gateway believes it holds per ERC-20 (a "virtual balance" ledger), and reconcile/verify it independently of externally-controllable `balanceOf` return values, or
- Restrict `order.inputs[i].token` to an allow-list of vetted tokens (as is common in intents/bridge designs) so arbitrary malicious token contracts cannot be escrowed at all, or
- At minimum, cap the credited `received`/delta to `min(requestedAmount, balanceOf_delta)` and additionally verify via `transferFrom`'s return-based accounting (SafeERC20 already does this for the call outcome, but not for the balance snapshot pattern) rather than solely a before/after `balanceOf` diff on an unvalidated token address.

### Proof of Concept
1. Attacker deploys `EvilToken` implementing `IERC20` where `balanceOf(gateway)` returns `0` on the first call in a transaction and an attacker-chosen large value `X` on the second call (e.g., toggled by an internal flag set during `transferFrom`).
2. Attacker calls `IntentGatewayV2.placeOrder` with `order.inputs[0] = {token: EvilToken, amount: X}`, approving `X` EvilTokens (which can even be `0`-cost mint to self).
3. In `placeOrder`, `balBefore = balanceOf(gateway) == 0`; `safeTransferFrom` executes (transferring little/nothing real, toggling the flag); `balanceOf(gateway)` now returns `X`; `order.inputs[0].amount = X - 0 = X`.
4. `_orders[commitment][EvilToken] = X` is credited into escrow though the gateway holds no real value.
5. A solver (or the attacker acting as solver) calls `fillOrder`, sending real `order.output` assets to the beneficiary and receiving `X` "EvilToken" from `_withdraw`'s `safeTransfer`, which the malicious token's `transfer` function can make succeed trivially (e.g., always returns `true`).
6. The solver has paid real value and received a worthless token; the protocol accounting shows `X` improperly escrowed and released.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L273-329)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L337-373)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
