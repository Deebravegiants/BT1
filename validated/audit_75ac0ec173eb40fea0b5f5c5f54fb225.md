## Title
Solver-selection signature is bound only to `(commitment, solver)`, not to the bid's fill terms — a selected solver can execute a worse fill than the one the user reviewed and authorized - (File: `evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/apps/IntentGatewayV2.sol`, `evm/src/apps/intentsv2/SolverAccount.sol`)

### Summary
IntentGatewayV2's solver-selection scheme authorizes a solver to fill an order using an EIP-712 `SolverSelection` message that only commits to `(commitment, solver)`. It never binds the user's authorization to the actual `FillOptions` (output amounts, fees) that were displayed off-chain during the bidding auction and that the user believed they were approving. This is structurally identical to the Nouns analog: a "vote" (the session-key authorization) is bound to an identifier, not to the content the voter actually reviewed, letting the authorized party substitute different content after authorization without the user's knowledge.

### Finding Description
The selection flow is:
1. Solvers post `PackedUserOperation` bids containing a `fillOrder(order, options)` call, where `options.outputs` are the amounts they offer. `userOpHash` (covering `callData`) is signed only by the solver — see `evm/src/apps/intentsv2/SolverAccount.sol:103-140`.
2. The user reviews bids off-chain (`BIDS_RECEIVED`) and picks the best one, then signs an EIP-712 `SolverSelection(commitment, solver)` message with the disposable session key:
```solidity
bytes32 structHash = keccak256(abi.encode(SELECT_SOLVER_TYPEHASH, options.commitment, options.solver));
``` [1](#0-0) 
3. `_select` stores `tstore(commitment, keccak256(abi.encode(options.solver, sessionKey)))` — again keyed only by solver address, not by the fill terms.
4. `fillOrder` re-derives `expectedSelectionHash = keccak256(abi.encode(msg.sender, order.session))` and compares it to the transient value: [2](#0-1) 

The session signature the user produces authorizes *any* fill by that solver address for that commitment — it says nothing about `options.outputs`, `options.relayerFee`, or `options.nativeDispatchFee`. The only cryptographic tie between the reviewed bid and the executed `fillOrder` call is the solver's own signature over `userOpHash` (which the solver controls and can re-sign at will), plus the nonce-key binding to `(commitment, sessionKey)` — none of which constrain the fill terms to what the user actually reviewed and picked. The user's `Bid.execute()` SDK path happens to resubmit the exact `userOp` object it displayed to the user, [3](#0-2) , but that is a client-side convention, not an on-chain guarantee: nothing on-chain prevents the selected solver from building a *different* `fillOrder(order, options')` with less favorable `options'.outputs`, signing it with their own key (which they control), and getting it accepted with the same session signature, since `select()`/`fillOrder()` never re-check the outputs against anything the user actually signed.

The only floor that is enforced is `order.output.assets` from the immutable `order` (checked for array-length only in the shown snippet, with the doc comment stating solver outputs "must be strictly >= the amounts requested in `order.output.assets`" [4](#0-3) ). That floor is a static, order-time value chosen by the user before any bidding occurred — it does not protect the delta between the *quoted, reviewed bid* and the *minimum acceptable* amount. Once a solver is selected based on an attractive quoted price, they retain full latitude to deliver anything down to that floor instead, and the session signature offers no additional protection against this bait-and-switch.

### Impact Explanation
This is the direct analog of the reported bug class: the authorization primitive (`SolverSelection`/session signature) is bound to an identifier (`commitment`, `solver`) instead of the content the counterparty actually evaluated (the fill terms). A malicious or opportunistic solver, once selected off a favorable quoted bid, can deliver a materially worse fill — down to the order's floor — without ever needing renewed user consent, extracting the difference (spread) between the quoted bid and the floor as unauthorized value for themselves. For large orders this can represent a meaningful, unauthorized transfer of value away from the intended beneficiary, without any additional signature or check preventing it.

### Likelihood Explanation
Moderate: it requires a solver willing to act adversarially after being selected (or a race to swap in worse terms using the same session signature before an honest submission lands), and the floor still limits the magnitude of loss to `bid_amount - order.output.assets`. This mirrors the "Won't Fix"-adjacent judgment in the original Nouns report (low likelihood, but the root cause — content unbound from authorization — is real and structurally present), which is why this is best assessed as Medium risk rather than Critical.

### Recommendation
Bind the `SolverSelection` EIP-712 message (and/or the transient-storage selection hash) to the specific fill terms the user reviewed — e.g. include a hash of `options.outputs`, `options.relayerFee`, and `options.nativeDispatchFee` in the signed struct, and re-derive/compare that hash inside `fillOrder` against the options actually supplied at execution time. This closes the gap between "authorization" and "content," analogous to the report's recommendation to make votes binding on proposal description/transactions rather than only the proposal identifier.

### Proof of Concept
1. Solver A posts a bid: `fillOrder(order, FillOptions{outputs: X})` where `X` is generous, signed with `solverSignatureA` over `userOpHashA` (covering `X`).
2. User reviews bids off-chain, selects Solver A based on `X`, and signs `SolverSelection(commitment, solverA)` with the session key — note this signature says nothing about `X`.
3. Solver A (or anyone who can induce the same session signature to be attached to a different UserOp, e.g. via mempool observation before the honest submission lands) constructs a new `fillOrder(order, FillOptions{outputs: Y})` with `Y` strictly less than `X` but still `>= order.output.assets`, signs it with their own solver key (`solverSignatureA'` over the new `userOpHashA'`), and submits it with nonce key still equal to `keccak256(commitment ‖ sessionKey)`.
4. `SolverAccount.validateUserOp` succeeds: solver signature is valid over its own `userOpHash`, nonce key matches, and `select()`/`fillOrder()`'s transient-storage check only compares `(msg.sender, order.session)`, which is unchanged.
5. `fillOrder` executes with `Y` instead of `X`; the user receives the degraded output with no additional authorization required.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L560-572)
```text
    function _select(SelectOptions calldata options) internal returns (address) {
        bytes32 structHash = keccak256(abi.encode(SELECT_SOLVER_TYPEHASH, options.commitment, options.solver));
        bytes32 digest = _hashTypedDataV4(structHash);
        address sessionKey = ECDSA.recover(digest, options.signature);

        bytes32 commitment = options.commitment;
        bytes32 selectionHash = keccak256(abi.encode(options.solver, sessionKey));
        assembly {
            tstore(commitment, selectionHash)
        }

        return sessionKey;
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L462-472)
```text
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

**File:** sdk/packages/sdk/src/protocols/intents/Bid.ts (L96-127)
```typescript
	/**
	 * Resolves the session key, signs the `SelectSolver` message for this bid's
	 * solver, and caches the signature. Signs at most once per bid.
	 *
	 * @throws If the session key is missing or signing fails.
	 */
	private async signSelection(): Promise<HexString> {
		if (this.cachedSignature) return this.cachedSignature

		const commitment = this.order.id as HexString
		const sessionKeyAddress = this.order.session as HexString

		const sessionKeyData = this.sessionPrivateKey
			? { privateKey: this.sessionPrivateKey }
			: await this.ctx.sessionKeyStorage.getSessionKeyByAddress(sessionKeyAddress)
		if (!sessionKeyData) {
			throw new Error(`SessionKey not found for commitment: ${commitment}`)
		}

		const signature = await CryptoUtils.signSolverSelection(
			commitment,
			this.solverAddress,
			this.domainSeparator,
			sessionKeyData.privateKey,
		)
		if (!signature) {
			throw new Error("Failed to sign solver selection")
		}

		this.cachedSignature = signature
		return signature
	}
```

**File:** sdk/packages/core/contracts/apps/IntentGatewayV2.sol (L148-167)
```text
struct FillOptions {
    /// @dev The fee paid in feeTokens to the relayer for processing transactions.
    uint256 relayerFee;
    /// @dev The fee paid in native tokens for cross-chain dispatch.
    uint256 nativeDispatchFee;
    /// @dev Last block number at which this fill may be executed. Zero means no bound.
    ///
    /// @dev A solver bidding through the coprocessor signs this calldata and then has no
    /// further say in when it is used: the order's `deadline` is chosen by the placer with
    /// no upper limit, and retracting the bid on Hyperbridge does not reach this chain. The
    /// placer holds the session key, so without a bound here they may sit on a signed bid
    /// and execute it whenever the price has moved in their favour. Setting this caps how
    /// long the quoted price stands.
    ///
    /// @dev Denominated in blocks, matching `order.deadline`, so both are read against the
    /// same clock (`_blockNumber()`, which is the L2 block number where that differs).
    uint256 validUntil;
    /// @dev The output tokens with amounts the solver is willing to give
    /// @dev Must be strictly >= the amounts requested in order.output.assets
    TokenInfo[] outputs;
```
