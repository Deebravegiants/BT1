### Title
Bid selection sums multi-leg output values as a single aggregate basket instead of per-leg, letting a solver's bid rank "best" while shorting a high-value leg - ([File: sdk/packages/sdk/src/protocols/intents/BidManager.ts])

### Summary
`BidManager.sortAllStables`, `sortMixedOutputs`, and their fallback `sortByRawAmountFallback` rank competing solver bids for a multi-output intent order by summing the value (or in the fallback case, the *raw token amount*) of every output leg into one aggregate number, and comparing that aggregate against the order's total required value. This mirrors the reported vault bug class: values of different tokens (and, in the fallback path, different decimals) are added together as if fungible, even though the underlying `IntentGatewayV2`/`IntrinsicIntents` settlement contracts treat each `inputs[i]`/`output.assets[i]` pair as an independent 1:1 leg.

### Finding Description
`sortBids` dispatches multi-output orders to `sortAllStables` or `sortMixedOutputs`, both of which compute a single `usdValue`/`bidUsd` for the entire bid and compare it only against the aggregate `requiredUsd`: [1](#0-0) 

Nothing in this comparison checks that each individual output token in the bid meets its own required amount — only that the sum across all output tokens clears the sum of all requirements. The same aggregate-only pattern repeats in `sortMixedOutputs`: [2](#0-1) 

When DEX pricing fails, the code falls back to `sortByRawAmountFallback`, which is worse: it sums raw `matching.amount` values across tokens with no decimal normalization and no price at all, then ranks bids by that raw total: [3](#0-2) 

This is used directly by the autopilot path `selectAndExecuteBest`, which sorts bids with `sortBids` and executes the top-ranked one that passes simulation: [4](#0-3) 

The on-chain settlement contracts, by contrast, treat each output leg independently, computing `totalRequired`, `solverAmount`, and the corresponding proportional escrow release per output index rather than as an aggregate basket: [5](#0-4) [6](#0-5) 

Because a solver's bid is free to allocate value however it likes across legs (e.g., pay the full/excess amount on a cheap or high-decimal-count token and under-deliver on the token the user actually values most), the aggregate comparison in `sortAllStables`/`sortMixedOutputs`/`sortByRawAmountFallback` can rank such a bid as the "best" or "fully covering" bid even though a specific, valuable leg is left unfilled or only partially filled — exactly the pattern in the referenced report where "the total balance should NOT be simply added from different tokens' tokenAmounts."

### Impact Explanation
The consumer of `sortBids`/`selectAndExecuteBest` is the order-placing user's own tooling (autopilot), used to automatically pick and sign off on the solver bid to execute. A malicious or opportunistic solver that understands this heuristic can craft a bid that appears to satisfy (or exceed) the order in aggregate while deliberately shorting the leg the user cares about most, get selected as the top bid, and have it executed. Because settlement is per-leg on-chain, the user does not lose escrowed input outright, but they receive a materially worse outcome than an available alternative bid would have given them (partial or degraded fill on the valuable leg while a cheap/high-decimal leg is padded), and a shady solver is preferentially routed to fill orders over more honest competitors, extracting value that should have gone to the user. In the raw-amount fallback (`sortByRawAmountFallback`), the lack of decimal normalization compounds this: a bid overpaying in an 18-decimal token trivially dominates the raw sum versus a bid paying correctly in a 6-decimal, high-value token, systematically biasing autopilot selection toward economically worse bids.

### Likelihood Explanation
`sortMixedOutputs` falls back to the unnormalized raw-sum path whenever DEX pricing for any output token fails (e.g., illiquid/exotic token, or a chain/token pair the swap helper can't quote) — a fairly common condition for non-major-pair orders — and `sortAllStables`/`sortMixedOutputs` always use aggregate, not per-leg, comparisons regardless of pricing success. Any solver bidding on a multi-output order can exploit this without any special access; it is a pure off-chain bid-construction strategy.

### Recommendation
Validate and rank bids per-output-leg rather than by an aggregate sum: require that each `output.assets[i]` is met (or proportionally scored) individually, and only use a combined score as a tiebreaker across bids that each satisfy every required leg. In `sortByRawAmountFallback`, at minimum normalize by each token's decimals before summing, and reject/deprioritize bids that under-deliver on any single required leg rather than allowing a surplus on one leg to mask a shortfall on another.

### Proof of Concept
1. User places a same-chain order with two output legs: leg A requires 1 WBTC (8 decimals, high USD value) and leg B requires 100,000 units of an 18-decimal low-value token (e.g., some reward token worth $0.0001).
2. DEX pricing for the reward token fails (thin liquidity), so `sortMixedOutputs` falls back to `sortByRawAmountFallback` (`BidManager.ts:396-398`).
3. Solver X bids: 0 WBTC (or far below required) + 5,000,000 units of the reward token — a raw sum that is enormous compared to Solver Y's honest bid of 1 WBTC + 100,000 reward tokens (raw sum dominated by the 8-decimal WBTC amount being numerically tiny next to 18-decimal token units).
4. `sortByRawAmountFallback` (`BidManager.ts:437-485`) ranks Solver X's bid above Solver Y's because it only compares `totalOffered` (unnormalized raw amounts) — Solver X's bid is selected by `selectAndExecuteBest` and executed first.
5. On-chain, the WBTC leg is left unfilled or only partially filled (`IntrinsicIntents.sol:73-118`), leaving the user's most valuable leg unfulfilled while a materially better bid (Solver Y's) was available and was skipped.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L185-222)
```typescript
	async selectAndExecuteBest(order: Order, bids: Bid[]): Promise<SelectBidResult> {
		const commitment = order.id as HexString
		console.log(`[BidManager] selectAndExecuteBest called for commitment=${commitment}, ${bids.length} bid(s)`)

		if (!this.ctx.bundlerUrl) {
			throw new Error("Bundler URL not configured")
		}
		if (!this.ctx.intentsCoprocessor) {
			throw new Error("IntentsCoprocessor required")
		}

		const sortedBids = await this.sortBids(order, bids)
		console.log(`[BidManager] ${sortedBids.length}/${bids.length} bid(s) passed validation and sorting`)
		if (sortedBids.length === 0) {
			throw new Error("No valid bids found")
		}

		console.log(`[BidManager] Simulating ${sortedBids.length} sorted bid(s) to find a valid one`)
		let simulationFailures = 0
		let executionFailures = 0
		for (let idx = 0; idx < sortedBids.length; idx++) {
			const bid = sortedBids[idx]
			console.log(`[BidManager] Simulating bid ${idx + 1}/${sortedBids.length} from solver=${bid.solverAddress}`)

			try {
				await bid.simulate()
			} catch (err) {
				simulationFailures += 1
				console.warn(
					`[BidManager] Bid ${idx + 1} from solver=${bid.solverAddress}: simulation FAILED: ` +
						`${err instanceof Error ? err.message : String(err)}`,
				)
				continue
			}

			console.log(`[BidManager] Bid ${idx + 1} from solver=${bid.solverAddress}: simulation PASSED`)
			try {
				return await bid.execute()
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L357-386)
```typescript
	private sortAllStables(bids: Bid[], orderOutputs: TokenInfo[], chainId: string): Bid[] {
		const requiredUsd = this.computeStablesUsdValue(orderOutputs, chainId)
		console.log(`[BidManager] sortAllStables: required USD value=${requiredUsd.toString()}`)

		const validBids: { bid: Bid; usdValue: Decimal }[] = []

		for (const bid of bids) {
			const bidUsd = this.computeStablesUsdValue(bid.outputs, chainId)

			if (bidUsd === null) {
				console.warn(`[BidManager] Bid from solver=${bid.solverAddress} REJECTED: unable to compute USD value`)
				continue
			}

			if (bidUsd.lt(requiredUsd)) {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress}: partial fill candidate ` +
						`(bid=${bidUsd.toString()}, required=${requiredUsd.toString()}, ` +
						`covers=${bidUsd.div(requiredUsd).mul(100).toFixed(2)}%)`,
				)
			} else {
				console.log(`[BidManager] Bid from solver=${bid.solverAddress} ACCEPTED: USD value=${bidUsd.toString()}`)
			}

			validBids.push({ bid, usdValue: bidUsd })
		}

		validBids.sort((a, b) => b.usdValue.comparedTo(a.usdValue))
		return validBids.map(({ bid }) => bid)
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L393-429)
```typescript
	private async sortMixedOutputs(bids: Bid[], orderOutputs: TokenInfo[], chainId: string): Promise<Bid[]> {
		const requiredUsd = await this.computeOutputsUsdValue(orderOutputs, chainId)

		if (requiredUsd === null) {
			console.warn("[BidManager] sortMixedOutputs: output tokens unpriceable, falling back to raw-amount sort")
			return this.sortByRawAmountFallback(bids, orderOutputs)
		}

		console.log(`[BidManager] sortMixedOutputs: required USD value=${requiredUsd.toString()}`)
		const validBids: { bid: Bid; usdValue: Decimal }[] = []

		for (const bid of bids) {
			const bidUsd = await this.computeOutputsUsdValue(bid.outputs, chainId)

			if (bidUsd === null) {
				console.warn(`[BidManager] Bid from solver=${bid.solverAddress} REJECTED: unable to price mixed outputs`)
				continue
			}

			if (bidUsd.lt(requiredUsd)) {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress}: partial fill candidate ` +
						`(bid=${bidUsd.toString()}, required=${requiredUsd.toString()}, ` +
						`covers=${bidUsd.div(requiredUsd).mul(100).toFixed(2)}%)`,
				)
			} else {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress} ACCEPTED: mixed USD value=${bidUsd.toString()}`,
				)
			}

			validBids.push({ bid, usdValue: bidUsd })
		}

		validBids.sort((a, b) => b.usdValue.comparedTo(a.usdValue))
		return validBids.map(({ bid }) => bid)
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L437-485)
```typescript
	private sortByRawAmountFallback(bids: Bid[], orderOutputs: TokenInfo[]): Bid[] {
		console.log(
			`[BidManager] sortByRawAmountFallback: checking ${bids.length} bid(s) against ${orderOutputs.length} required output(s)`,
		)
		const validBids: { bid: Bid; totalOffered: Decimal }[] = []

		for (const bid of bids) {
			let valid = true
			let totalOffered = new Decimal(0)
			let rejectReason = ""

			for (const required of orderOutputs) {
				const matching = bid.outputs.find((o) => o.token.toLowerCase() === required.token.toLowerCase())
				if (!matching) {
					valid = false
					rejectReason = `missing output token=${required.token}`
					break
				}
				totalOffered = totalOffered.plus(new Decimal(matching.amount.toString()))
			}

			if (!valid) {
				console.warn(`[BidManager] Bid from solver=${bid.solverAddress} REJECTED (fallback): ${rejectReason}`)
				continue
			}

			const totalRequired = orderOutputs.reduce(
				(acc, o) => acc.plus(new Decimal(o.amount.toString())),
				new Decimal(0),
			)

			if (totalOffered.lt(totalRequired)) {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress}: partial fill candidate (fallback) ` +
						`(offered=${totalOffered.toString()}, required=${totalRequired.toString()}, ` +
						`covers=${totalOffered.div(totalRequired).mul(100).toFixed(2)}%)`,
				)
			} else {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress} ACCEPTED (fallback): totalOffered=${totalOffered.toString()}`,
				)
			}

			validBids.push({ bid, totalOffered })
		}

		validBids.sort((a, b) => b.totalOffered.comparedTo(a.totalOffered))
		return validBids.map(({ bid }) => bid)
	}
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L65-118)
```text
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

            if (totalRequired > amountFilled) isFullyFilled = false;
            if (protocolShare > 0) emit DustCollected(token, protocolShare);

            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
            outputFills[i] = TokenInfo({token: outputToken, amount: fillAmount});
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L171-199)
```text
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }
```
