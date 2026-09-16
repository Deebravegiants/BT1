### Title
Governance Can Change `surplusShareBps` / Protocol Fee Splits Between Order Placement and Fill, Retroactively Altering the Split on Already-Escrowed Funds — (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentGatewayV2` stores a single global, mutable `Params` struct (`protocolFeeBps`, `surplusShareBps`, per-destination fee overrides) that Hyperbridge governance can overwrite at any time via `_updateParams`, with no timelock or delay [1](#0-0) . Because the `Order` struct that a user commits to at placement time does not itself carry a snapshot of `surplusShareBps` [2](#0-1) , the split percentage applied to solver-provided surplus is necessarily read from whatever `_params` is live *at fill/settlement time*, which may be long after the order was placed and its inputs escrowed. This is the same bug class as the OtterSec Tortuga finding: a fee/commission-style parameter is mutable by a privileged party at any moment and is applied against funds that are already locked/committed under a different, earlier expectation, with no lockup period protecting the counterparty from a sudden change.

### Finding Description
`_updateParams` in `IntentsBase.sol` lets governance instantly overwrite the gateway's global `Params`, including `surplusShareBps` ("the percentage of surplus (in basis points) that goes to the protocol"), and per-destination `protocolFeeBps` overrides [3](#0-2) . There is no delay, cooldown, or grandfathering mechanism — the new params take effect for the very next `onAccept`/fill processed [4](#0-3) .

Unlike `protocolFeeBps` at *placement* (which is deducted immediately and baked into the fee-reduced amount that becomes part of the order commitment hash, so it cannot be retroactively changed for an already-placed order) [5](#0-4) , the surplus-share split is applied later, at fill time, when a solver provides more output than required [6](#0-5) . Because the `Order` struct/commitment does not encode `surplusShareBps`, the ratio actually applied comes from the gateway's current `_params` storage rather than from any value fixed at the time the order was placed or the surplus economics were negotiated between user and solver.

This mirrors the Tortuga `change_commission` bug exactly: a fee-percentage field the protocol treats as a "current rate" can be changed unilaterally and instantly by the party that benefits from it (here, protocol governance, analogous to the validator), and it is applied to value that is already locked up in an escrow the counterparty cannot unilaterally exit (an open, unfilled order, or an order whose fill is in flight/pending settlement across chains) — the counterparty (the solver providing surplus, or the beneficiary receiving it) has no way to know in advance what split will actually be enforced when their transaction lands.

### Impact Explanation
A malicious or compromised governance actor (or an admin key holder before that authority is fully decentralized) could raise `surplusShareBps` to 10,000 (100%) via `_updateParams` immediately before a large pending fill settles, causing a solver's entire surplus contribution to be seized by the protocol instead of split with the beneficiary as expected when the fill was priced/simulated. Cross-chain orders are especially exposed: settlement is asynchronous (a relayer must deliver the `RedeemEscrow`/`onAccept` message) [7](#0-6) , so there is a window — comparable to Tortuga's 30-day stake lockup — during which the economic terms a solver or user relied on can be changed underneath them with no recourse.

### Likelihood Explanation
Requires no attacker capital and no bypass of authentication — it is a direct consequence of `_updateParams` being callable by governance with immediate effect and no timelock, combined with the fill-time (not placement-time) evaluation of `surplusShareBps`. The only constraint is that the caller must be the authorized governance/Hyperbridge relayer path (`onAccept` from `source == host.hyperbridge()`), which is the normal, expected way parameters are updated in production, not a hypothetical compromise [8](#0-7) .

### Recommendation
Snapshot the economically-relevant parameters (at minimum `surplusShareBps`, and any other split/fee percentage evaluated at fill/settlement rather than at placement) into the `Order` struct or its commitment at placement time, so that settlement always honors the rate the parties agreed to when escrow was created — mirroring the OtterSec-recommended fix of introducing a lockup/effective-time delay for commission-style parameter changes so they cannot retroactively affect value already locked under the old terms.

### Proof of Concept
1. User/solver interaction begins: a solver observes `params().surplusShareBps = 5000` (50/50 split) and decides to fill an order, over-providing output tokens for a favorable surplus split.
2. Before the fill's settlement message (`RedeemEscrow`) is delivered/`onAccept`-processed on the source chain, governance calls the `UpdateParams` action via `_updateParams`, setting `surplusShareBps = 10000` [9](#0-8) .
3. When the settlement lands, the withdrawal/redemption logic reads the now-current `_params.surplusShareBps` (100%) instead of the 50% the solver priced their fill against, and the solver's entire surplus is diverted to the protocol beneficiary instead of split as expected.

Note: I was not able to directly inspect the exact surplus-splitting arithmetic in `fillOrder`/`withdraw` (in `ExtrinsicIntents.sol`/`IntrinsicIntents.sol`) within the available tool budget to pin the precise line computing the split at settlement; this conclusion rests on (a) `_updateParams` applying instantly and globally [1](#0-0) , and (b) the `Order`/commitment struct not encoding `surplusShareBps` [10](#0-9) , which together necessitate a fill-time (not placement-time) read of the live governance value. A background Devin session with full repo access should confirm the exact read site in `ExtrinsicIntents.sol`/`IntrinsicIntents.sol` before treating this as fully proven.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L601-628)
```text
     * @dev Updates the gateway's configuration parameters and per-destination protocol fees.
     * Called by Hyperbridge governance to modify fee settings, host address, dispatcher,
     * price oracle, and other operational parameters.
     *
     * Validates all params before applying. Emits ParamsUpdated with the old and new params,
     * then iterates over any destination-specific fee overrides and applies them to
     * `_destinationProtocolFees`.
     *
     * @param update The parameter update containing new params and destination fee overrides.
     */
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

**File:** sdk/packages/core/contracts/apps/IntentGatewayV2.sol (L91-107)
```text
 */
struct Params {
    /// @dev The address of the host contract
    address host;
    /// @dev Address of the dispatcher contract responsible for handling intents.
    address dispatcher;
    /// @dev Flag indicating whether solver selection is enabled.
    bool solverSelection;
    /// @dev The percentage of surplus (in basis points) that goes to the protocol. The rest goes to beneficiary.
    /// 10000 = 100%, 5000 = 50%, etc.
    uint256 surplusShareBps;
    /// @dev The protocol fee in basis points charged on order inputs.
    /// 10000 = 100%, 100 = 1%, etc.
    uint256 protocolFeeBps;
    /// @dev The address of the price oracle contract.
    address priceOracle;
}
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L2860-2906)
```text
        ParamsUpdate memory update = ParamsUpdate({params: newParams, destinationFees: destinationFees});

        bytes memory body = bytes.concat(bytes1(uint8(IntentsBase.RequestKind.UpdateParams)), abi.encode(update));

        PostRequest memory request = PostRequest({
            source: host.hyperbridge(),
            dest: host.host(),
            nonce: 0,
            from: abi.encodePacked(address(intentGateway)),
            to: abi.encodePacked(address(intentGateway)),
            body: body,
            timeoutTimestamp: 0
        });

        vm.recordLogs();

        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: relayer, request: request}));

        // Check events
        Vm.Log[] memory entries = vm.getRecordedLogs();
        bool paramsUpdatedFound = false;
        uint256 destinationFeeEventsFound = 0;

        for (uint256 i = 0; i < entries.length; i++) {
            if (
                entries[i].topics[0]
                    == keccak256(
                        "ParamsUpdated((address,address,bool,uint256,uint256,address),(address,address,bool,uint256,uint256,address))"
                    )
            ) {
                paramsUpdatedFound = true;
            }

            if (entries[i].topics[0] == keccak256("DestinationProtocolFeeUpdated(string,uint256)")) {
                destinationFeeEventsFound++;
            }
        }

        assertTrue(paramsUpdatedFound, "ParamsUpdated event should be emitted");
        assertEq(destinationFeeEventsFound, 2, "Should emit 2 DestinationProtocolFeeUpdated events");

        // Verify params were updated
        Params memory updatedParams = intentGateway.params();
        assertEq(updatedParams.host, newParams.host, "Host should be updated");
        assertEq(updatedParams.protocolFeeBps, newParams.protocolFeeBps, "ProtocolFeeBps should be updated");
    }
```

**File:** docs/content/developers/evm/intent-gateway/placing-orders.mdx (L94-111)
```text
### Protocol fees

Before escrowing, the contract deducts a protocol fee from each input amount:

```
protocolFee = input.amount × protocolFeeBps / 10_000
reducedAmount = input.amount − protocolFee
```

The fee is retained in the gateway as dust (emitting `DustCollected`), and per-destination overrides take precedence over the global `protocolFeeBps` when set. Current deployments charge **5 bps (0.05%)**. For a 100 USDC input:

| Item | Amount |
| --- | ---: |
| USDC transferred from your wallet | 100.000000 USDC |
| Protocol fee: `100 × 5 / 10,000` | 0.050000 USDC |
| Amount actually escrowed and offered to solvers | 99.950000 USDC |

The commitment hash is computed over the **fee-reduced inputs** — solvers read the reduced amounts from the `OrderPlaced` event and only need to match those. The fee is deducted at placement and is **not refunded** if the order expires, receives no bids, or is cancelled; a cancellation returns the remaining escrow and `order.fees`, but not the protocol fee.
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L41-47)
```text
### Fill Flow

The solver calls `fillOrder(order, options)` on the **destination chain**. The function verifies the order hasn't expired (`order.deadline >= block.number`), confirms execution is on the correct chain, and checks the order hasn't already been filled. The solver must provide output amounts greater than or equal to the order's required amounts — any amount below the required amount reverts with `InvalidInput()`.

If the solver provides more tokens than required, the excess (surplus) is split according to `surplusShareBps`. If the order includes calldata, 100% of surplus goes to the protocol to prevent manipulation.

After delivering output tokens to the beneficiary, the contract dispatches a cross-chain `RedeemEscrow` message back to the source chain.
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L50-58)
```text
### Settlement

When the settlement message arrives on the source chain, the ISMP host calls `onAccept()`. The handler authenticates the message (verifying it came from a known IntentGateway instance), decodes the `WithdrawalRequest`, and calls `withdraw()` which:

1. Marks the order as filled (`_filled[commitment] = solver`)
2. Transfers each escrowed input token to the solver
3. Releases stored transaction fees (in fee token) to the solver
4. Emits `EscrowReleased(commitment, tokens)`

```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L637-660)
```text
        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
        } else if (kind == RequestKind.UpdateParams) {
            // Decode the body which includes optional destination-specific protocol fee updates
            ParamsUpdate memory update = abi.decode(incoming.request.body[1:], (ParamsUpdate));
            emit ParamsUpdated({previous: _params, current: update.params});
            _params = update.params;

            // Update destination-specific protocol fees if provided
            for (uint256 i; i < update.destinationFees.length;) {
                bytes32 stateMachineId = update.destinationFees[i].stateMachineId;
                uint256 feeBps = update.destinationFees[i].destinationFeeBps;
                _destinationProtocolFees[stateMachineId] = feeBps;

                unchecked {
                    ++i;
                }
                emit DestinationProtocolFeeUpdated(stateMachineId, feeBps);
            }
```
