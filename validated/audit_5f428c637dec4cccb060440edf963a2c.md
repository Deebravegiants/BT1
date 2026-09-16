### Title
Governance parameter update (`host`) can strand or misdirect escrowed transaction fees before settlement - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._updateParams()` allows Hyperbridge governance to change `_params.host` (and other params) at any time, but `_withdraw()` resolves the fee token to transfer accrued "transaction fees" by calling `IDispatcher(host()).feeToken()` **at withdrawal time**, not the fee token that was actually escrowed when the order was placed. This is the same bug class as the reported `CouncilMember` issue: a parameter/state change is not preceded by settling ("retrieving") the funds accrued under the old configuration, so those funds are stranded once the configuration changes.

### Finding Description
`_updateParams` mutates `_params` (including `host`) in place with no check that outstanding per-order escrowed fee balances have been reconciled against the fee token implied by the new host: [1](#0-0) 

`host()` is a live getter over `_params.host`: [2](#0-1) 

When an order is finalized, any amount recorded under the `TRANSACTION_FEES` sentinel key in `_orders[commitment][...]` is transferred using whatever `IDispatcher(host()).feeToken()` currently resolves to — a dynamic, present-tense lookup rather than the fee token that was actually deposited into escrow at order-placement time: [3](#0-2) 

If governance rotates `_params.host` to an `EvmHost` instance configured with a different `feeToken` (hosts can independently configure/rotate their `feeToken`, see `EvmHost.updateHostParamsInternal`), any order whose `TRANSACTION_FEES` balance was escrowed in the *old* fee token becomes unreachable through the normal withdrawal path: `_withdraw` will attempt `safeTransfer` of the *new* fee token, which the contract either does not hold (revert / stuck order finalize) or — if it happens to hold some balance of the new token from unrelated activity — could transfer the wrong asset/amount to the beneficiary, corrupting fee accounting for other orders.

### Impact Explanation
This can permanently strand relayer/protocol fees that users prepaid when placing intents (`OrderPlaced.fees` / escrowed `TRANSACTION_FEES`), or cause an order's fee-transfer step to revert and block finalization, since the withdrawal logic never re-derives or migrates the escrowed amount to match a host/feeToken change. This is a fund-loss/fund-freezing bug directly reachable by any user who places an intent order before a routine (non-malicious) governance host-params update — exactly analogous to the `CouncilMember` report where changing stream parameters without first flushing accrued funds forfeits them.

### Likelihood Explanation
Governance parameter updates to `_params.host` are an expected, periodic operational action (e.g., host contract upgrades/migrations), not an attack. Any outstanding intent orders at the time of such an update are affected without any additional attacker action required, making the likelihood moderate-to-high over the contract's operational lifetime.

### Recommendation
Before or as part of `_updateParams` changing `_params.host` (or any change of the effective fee token), settle/snapshot outstanding `TRANSACTION_FEES` balances against the currently configured fee token, or store the fee token address alongside the escrowed amount at order-placement time so `_withdraw` always redeems using the token actually held, rather than dynamically querying `host().feeToken()` at withdrawal time.

### Proof of Concept
Conceptual, since the exact `placeOrder` implementation that populates `_orders[commitment][TRANSACTION_FEES]` (in `IntentGatewayV2.sol`/`IntrinsicIntents.sol`/`ExtrinsicIntents.sol`) could not be located via the available index/search tools — this is a limitation of the current codebase index, not evidence the function doesn't exist:
1. User places an intent order; protocol escrows `TRANSACTION_FEES` amount denominated in the fee token configured by the host at that time.
2. Before the order is filled/withdrawn, Hyperbridge governance calls `_updateParams` to rotate `_params.host` to a new `EvmHost` with a different `feeToken` configured.
3. Order finalization calls `_withdraw`, which reads `IDispatcher(host()).feeToken()` — now the new token — and attempts to transfer that token out for the `TRANSACTION_FEES` amount, either reverting (funds/order stuck) or transferring an unrelated token/balance. [4](#0-3) [5](#0-4)

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L366-368)
```text
    function host() public view virtual returns (address) {
        return _params.host;
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-485)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L611-628)
```text
    function _updateParams(ParamsUpdate memory update) internal {
        _validateParams(update.params);

        emit ParamsUpdated({previous: _params, current: update.params});
        _params = update.params;

        for (uint256 i; i < update.destinationFees.length;) {
            bytes memory chain = update.destinationFees[i].chain;
            uint256 feeBps = update.destinationFees[i].destinationFeeBps;
            if (feeBps >= 10_000) revert InvalidInput();
            _destinationProtocolFees[keccak256(chain)] = feeBps;

            unchecked {
                ++i;
            }
            emit DestinationProtocolFeeUpdated(string(chain), feeBps);
        }
    }
```
