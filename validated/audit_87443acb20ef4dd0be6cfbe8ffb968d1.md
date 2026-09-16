Based on my research, I found the closest analog in the codebase. It's a self-dealing points/rewards farming loop in the Intent Gateway indexer, structurally identical to the original C4 finding: an unprivileged actor (a "user" who is also an "intent solver") can act on both sides of an on-chain action to repeatedly earn protocol-level rewards, and the only defense against it (an address-equality check) is applied inconsistently and is only enforced off-chain for one of the three reward paths, not on the primary fill-reward path.

### Title
Self-fill of one's own intent order farms both placer and filler reward points indefinitely - ([File: sdk/packages/indexer/src/services/intentGatewayV3.service.ts])

### Summary
`IntentGatewayV2.placeOrder`/`fillOrder` impose no restriction preventing the order placer (`order.user`) from also being the solver (`msg.sender`) that fills the same order. The Hyperbridge indexer awards `ORDER_PLACED_POINTS` to the placer and `ORDER_FILLED_POINTS` to the filler for every order, valued by the order's USD volume. Because self-fill is unrestricted on-chain, and the indexer only rejects self-referral for the separate `REFERRER` bonus (not for the placer/filler double-award), a single address can repeatedly place and immediately fill its own same-chain orders, collecting both reward legs on every cycle for the cost of only the protocol fee (`protocolFeeBps`, as low as 0.05%) and gas — mirroring the original report's "copy your own portfolio to keep earning royalties" pattern of exploiting a fee/reward-sharing mechanism that never checks for self-dealing.

### Finding Description
`IntentGatewayV2.placeOrder` stamps `order.user = msg.sender` [1](#0-0)  and `fillOrder` allows any `msg.sender` to fill it (subject only to `solverSelection`, which is off by default and, even when on, is satisfied by the placer signing its own session key) [2](#0-1) . Nothing compares `order.user` to `msg.sender` in `fillOrder`, `_fillSameChain`, or `_fillCrossChain`.

Downstream, the indexer awards points keyed only by role, not by relationship between roles:
- On `OrderPlaced`, `ORDER_PLACED_POINTS` is credited to `order.user` for the full USD input value [3](#0-2) .
- On fill, `ORDER_FILLED_POINTS` is credited to `filler` for the same USD value [4](#0-3) .

The only self-dealing guard in the codebase is `resolveGraffiti`, which nulls out the `REFERRER` bonus when the graffiti tag equals the placer's own address [5](#0-4) . This guard covers only the third-party referral leg; it does nothing to stop `order.user == filler`, which is the path that actually pays out on every single order (placer + filler points), not just the optional referrer bonus.

This is structurally the same bug class as the external report: a value-sharing mechanism (royalty shares / reward points) has no check that the two counter-parties in a transaction are the same address, so a single actor can repeatedly transact with itself to harvest both sides of the reward split.

### Impact Explanation
An unprivileged actor with a single EOA can:
1. Place a same-chain order (`placeOrder`) with arbitrary `output`/`input` token pairs it fully controls both sides of.
2. Immediately call `fillOrder` from the same address, providing the exact required output amount to itself as beneficiary.
3. Receive `ORDER_PLACED_POINTS` + `ORDER_FILLED_POINTS`, both proportional to the order's USD volume, for a self-dealt transaction that transferred no real economic value between distinct parties.
4. Repeat indefinitely — cost is only the `protocolFeeBps` dust (as low as 5 bps per the docs) plus surplus-share dust if any, and gas.

Since reward points are the on-chain/indexed accounting basis for the protocol's participant-reward and (per `docs/POINTS_API.md`) leaderboard/airdrop-style attribution system, this lets a single wallet inflate its `ORDER_PLACED_POINTS`, `ORDER_FILLED_POINTS`, and (via a second, colluding wallet as beneficiary/referrer) `ORDER_REFERRED_POINTS`, diluting the reward pool at negligible cost to itself — the same "reduce/dilute a shared payout to near-zero economic cost via self-dealing" pattern the original report flagged, sustained by the C4 judge as a real disablement of a core economic mechanism.

### Likelihood Explanation
High. No special permissions, no governance access, and no cross-chain proof are required — the exploit is a same-chain `placeOrder` + `fillOrder` pair from one EOA, using tokens the attacker already owns. `solverSelection` is off by default in the deployed gateway params seen throughout the test suite, and even when enabled, the placer trivially satisfies it since it controls the session key. The economics (near-zero fee vs. unbounded repeatable point issuance) make this attractive to run at scale/automatically.

### Recommendation
- On-chain: optionally reject `fillOrder` when `order.user == bytes32(uint256(uint160(msg.sender)))`, or at minimum flag such fills distinctly in the `OrderFilled`/`PartialFill` events so downstream consumers can exclude them.
- Indexer: mirror the existing `resolveGraffiti` self-referral guard onto the placer/filler award path — skip or discount `ORDER_FILLED_POINTS` (and the associated `totalOrderFilledVolumeUSD`/`VolumeService` updates) whenever `filler == bytes32ToBytes20(orderPlaced.user)`.
- Consider rate-limiting or diminishing-returns curves per unique counterparty pair to blunt the residual Sybil path (two wallets trading back and forth), consistent with the original report's finding that a purely on-chain check cannot fully close a multi-wallet variant of this issue.

### Proof of Concept
1. Attacker wallet `A` calls `IntentGatewayV2.placeOrder(order, graffiti=0)` with `order.output.beneficiary = A`, escrowing `input` tokens it owns [6](#0-5) .
2. In the same or next transaction, `A` calls `fillOrder(order, options)` with `options.outputs` matching the required amount, sending output tokens from `A` back to `A` (`beneficiary == A == msg.sender`) via `_fillSameChain` [7](#0-6) .
3. The indexer's `orderPlacedV3` handler credits `A` with `ORDER_PLACED_POINTS` for the input USD value [8](#0-7) .
4. The indexer's fill handler credits `A` (as `filler`) with `ORDER_FILLED_POINTS` for the same USD value [9](#0-8) .
5. Repeat steps 1–4 in a loop; each cycle costs only `protocolFeeBps` dust, yielding unbounded, self-dealt reward-point accrual with no check anywhere in the on-chain contract or the indexer's placer/filler award path comparing `order.user` to `filler`.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-234)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
```

**File:** evm/src/apps/IntentGatewayV2.sol (L443-472)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
        uint256 blockNumber = _blockNumber();
        if (order.deadline < blockNumber) revert Expired();
        // The solver's own bound on how long its quoted price stands. Zero means unbounded,
        // which is the right default for a solver filling directly — it is only at risk from
        // its own staleness. It matters for a bid signed through the coprocessor, where the
        // order placer chooses the moment of execution and nothing else caps the wait.
        if (options.validUntil != 0 && blockNumber > options.validUntil) revert FillExpired();
        bytes32 commitment = keccak256(abi.encode(order));

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain && orderSource != currentChain) revert WrongChain();
        if (!isSameChain && orderDest != currentChain) revert WrongChain();

        if (_filled[commitment] != address(0)) revert Filled();

        if (_params.solverSelection) {
            bytes32 storedSelectionHash;
            assembly {
                storedSelectionHash := tload(commitment)
            }

            bytes32 expectedSelectionHash = keccak256(abi.encode(msg.sender, order.session));
            if (storedSelectionHash != expectedSelectionHash) revert Unauthorized();
        }
```

**File:** sdk/packages/indexer/src/services/intentGatewayV3.service.ts (L237-252)
```typescript
			logger.info("Now awarding points for the OrderV3 Placed Event")

			// Award points for order placement - using USD value directly
			const orderValue = new Decimal(inputUSD)
			const pointsToAward = orderValue.floor().toNumber()

			await PointsService.awardPoints(
				order.user,
				decodeChain(order.sourceChain),
				BigInt(pointsToAward),
				ProtocolParticipantType.USER,
				PointsActivityType.ORDER_PLACED_POINTS,
				transactionHash,
				`Points awarded for placing orderV3 ${order.id} with value ${inputUSD} USD`,
				timestamp,
			)
```

**File:** sdk/packages/indexer/src/services/intentGatewayV3.service.ts (L570-583)
```typescript
				const orderValue = new Decimal(orderPlaced.inputUSD.toString())
				const pointsToAward = orderValue.floor().toNumber()

				// Rewards
				await PointsService.awardPoints(
					filler,
					decodeChain(orderPlaced.destChain),
					BigInt(pointsToAward),
					ProtocolParticipantType.FILLER,
					PointsActivityType.ORDER_FILLED_POINTS,
					transactionHash,
					`Points awarded for filling orderV3 ${commitment} with value ${orderPlaced.inputUSD} USD`,
					timestamp,
				)
```

**File:** sdk/packages/indexer/src/handlers/events/intentGatewayV3/orderPlacedV3.event.handler.ts (L151-161)
```typescript
/**
 * Maps a raw graffiti value to the stored referrer tag: a graffiti equal to
 * the placing user's address is treated as unattributed (DEFAULT_REFERRER).
 */
function resolveGraffiti(graffitiArg: string, userAddress: string): Hex {
	if (graffitiArg.toLowerCase() === userAddress.toLowerCase()) return DEFAULT_REFERRER as Hex

	const graffiti = bytes20ToBytes32(graffitiArg) as Hex
	logger.info(`Using referrer graffiti: ${graffiti}`)
	return graffiti
}
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L53-106)
```text
    function _fillSameChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        bool isFullyFilled = true;

        TokenInfo[] memory escrowedInputs = new TokenInfo[](outputsLen);
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            uint256 alreadyFilled = _partialFills[commitment][outputToken];
            uint256 remaining = totalRequired - alreadyFilled;
            if (remaining == 0 || solverAmount == 0) {
                if (solverAmount == 0 && remaining > 0) isFullyFilled = false;
                continue;
            }
            uint256 fillAmount;

            uint256 beneficiaryShare = 0;
            uint256 protocolShare = 0;
            if (alreadyFilled == 0 && solverAmount > totalRequired) {
                fillAmount = totalRequired;
                (protocolShare, beneficiaryShare) =
                    _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);
            } else {
                fillAmount = solverAmount > remaining ? remaining : solverAmount;
            }

            uint256 amountFilled = alreadyFilled + fillAmount;
            _partialFills[commitment][outputToken] = amountFilled;
            uint256 beneficiaryTotal = fillAmount + beneficiaryShare;

            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
```
