### Title
Intents escrow accounting trusts nominal transfer amounts instead of actual received/held balances, causing insolvency and fund freezing with rebasing or fee-on-transfer tokens - (File: evm/src/apps/intentsv2/IntentsBase.sol, evm/src/apps/intentsv2/IntrinsicIntents.sol, evm/src/apps/intentsv2/ExtrinsicIntents.sol)

### Summary
`placeOrder`/`fillOrder` in the Intents v2 escrow (`IntrinsicIntents.sol`, `ExtrinsicIntents.sol`) credit a per-order, per-token ledger (`_orders[commitment][token]`) with the *nominal* input amount (minus protocol fee) immediately after calling `IERC20.safeTransferFrom`, without ever reconciling that figure against the contract's actual token balance. `_withdraw`/`withdraw` later pay out exactly that recorded ledger amount via `safeTransfer`, again with no live-balance check. Because every order's escrow entry for a given token address is served out of one shared token balance held by the contract, this is the same class of bug as the reported OpenQ issue: a static accounting snapshot (`fundingTotals` there, `_orders[commitment][token]` here) can silently diverge from the token's real, elastic balance.

### Finding Description
In `IntrinsicIntents.sol`/`ExtrinsicIntents.sol`, the escrow bookkeeping is:
```solidity
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
...
_orders[commitment][token] += reducedInputs[i].amount;
``` [1](#0-0) [2](#0-1) 

This assumes `amount` transferred in equals `amount` actually credited to the contract's balance and equals `amount` still held at withdrawal time. That assumption fails for:
- **Fee-on-transfer tokens** — the contract receives less than `order.inputs[i].amount`, but the ledger still records the full nominal amount.
- **Rebasing tokens** — even if the initial transfer is exact, a downward rebase between `placeOrder` and the eventual `withdraw`/`fillOrder`/`cancelOrder` call reduces the contract's actual `balanceOf(token)` while `_orders[commitment][token]` (and the sum of all such entries for that token across all outstanding orders) remains unchanged.

At withdrawal time, `_withdraw` transfers the *ledger* amount, not a live-balance-derived share:
```solidity
uint256 escrowed = _orders[body.commitment][token];
if (escrowed == 0) revert UnknownOrder();
_orders[body.commitment][token] = escrowed - amount;
IERC20(token).safeTransfer(beneficiary, amount);
``` [3](#0-2) 

Since the contract pools all orders' escrow for the same token address into one `balanceOf`, once the aggregate of live `_orders[*][token]` entries exceeds the token's actual on-chain balance, some subset of withdrawals will revert with insufficient balance (funds frozen for those users/solvers) while earlier claimants are paid in full out of what is effectively other users' escrowed collateral — the exact "someone overclaims at another's expense, or underclaims and funds are stuck" pattern described in the source report.

### Impact Explanation
- Users placing orders in a rebasing or fee-on-transfer token, or solvers filling such orders, can have their `RedeemEscrow`/`RefundEscrow`/`cancelOrder` calls permanently revert once the token's actual balance in the gateway falls below the sum of outstanding ledger entries — a **freezing of funds** for the affected order(s).
- Conversely, an order created with more nominal ledger credit than what is physically held effectively drains real balance backing *other* users' orders when it withdraws first, socializing the shortfall — a **loss of funds** for later claimants.
- This reaches every entry point that mutates or reads `_orders`: `placeOrder` (unprivileged, single transaction), `fillOrder` (solver-triggered), `cancelOrder`/`onGetResponse` (refund path), and the cross-chain `onAccept` withdraw path — all reachable without any privileged role.

### Likelihood Explanation
Likelihood is moderate: it requires the deployer/governance to whitelist a rebasing or fee-on-transfer ERC20 as an order input/output token (the contract does not restrict token type), which is plausible given the protocol's general-purpose token-swap design and no visible allow/deny-list logic for token elasticity in the reviewed code. Once such a token is in use, the divergence accumulates passively with every rebase or transfer, requiring no attacker action beyond normal usage.

### Recommendation
- On deposit, measure the contract's token balance before and after `safeTransferFrom` and credit `_orders[commitment][token]` with the actual delta received, not the nominal `order.inputs[i].amount`.
- On withdrawal, either (a) explicitly disallow rebasing/fee-on-transfer tokens via metadata checks or an allowlist, or (b) track escrow as a share of contract balance rather than a fixed absolute amount, re-deriving payouts from `balanceOf` at withdrawal time.
- Document/enforce that only standard, non-elastic ERC20 tokens are supported as `order.inputs`/`order.output.assets`, since Hyperbridge's on-chain context appears not to have accounted for elastic-supply tokens in this escrow design.

### Proof of Concept
1. Deployer configures a fee-on-transfer (or rebasing) ERC20 `T` as a valid input token for the Intents gateway (no code-level restriction prevents this).
2. User A calls `placeOrder` with `order.inputs[0] = {token: T, amount: 1000}`. `safeTransferFrom` moves tokens from A, but because `T` charges a transfer fee, the gateway's actual `T.balanceOf(gateway)` only increases by, say, 950. The ledger nonetheless records `_orders[commitmentA][T] = 990` (1000 minus protocol fee, per `reducedInputs`) — 40 more than what the contract actually holds for this order.
3. User B similarly places an order with the same token `T`, contributing another shortfall.
4. Solver fills order A; `fillOrder`/`onAccept` triggers `_withdraw`, which calls `safeTransfer(beneficiary, 990)` sourced from the shared `T` balance in the contract — succeeding only because it draws on token B's under-collateralized deposit as well.
5. When user B (or their solver) later attempts to withdraw/cancel, the gateway's `T.balanceOf(this)` is insufficient to cover `_orders[commitmentB][T]`, so `IERC20(T).safeTransfer` reverts, permanently freezing B's escrowed funds.

This demonstrates that a single unprivileged `placeOrder` transaction with an elastic-supply token is sufficient to desynchronize the escrow ledger from the real token balance, leading to fund freezing/loss for other order participants — the same root-cause class as the referenced OpenQ `TieredPercentageBountyV1` rebasing-token finding.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-469)
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
