Found the analog. It's the exact same bug class as the `experimental_requestSession` report: a caller-supplied commitment/hash value is trusted by a signature-verification function without checking that it actually corresponds to the real data (`Order`) it's supposed to represent.

### Title
Unverified `commitment` in `IntentsBase._select()` lets a solver bind a session-key authorization to a different order than the one the user actually signed - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`_select()` accepts a caller-supplied `options.commitment` and uses it directly to build the EIP-712 digest and as the transient-storage key, without ever checking that `options.commitment == keccak256(abi.encode(order))` for any real, on-chain order.

### Finding Description
`_select` computes `structHash = keccak256(abi.encode(SELECT_SOLVER_TYPEHASH, options.commitment, options.solver))`, recovers `sessionKey` from `options.signature`, and stores `tstore(commitment, keccak256(abi.encode(solver, sessionKey)))`: [1](#0-0) 

The `commitment` here is caller-controlled input from `SelectOptions calldata options` — it is never derived from, or checked against, any actual `Order` struct inside `select()`/`_select()`. The only place `commitment` is legitimately derived from order data is in `fillOrder`, via `bytes32 commitment = keccak256(abi.encode(order))`: [2](#0-1) 

`fillOrder` then reads `tload(commitment)` using *that locally recomputed* commitment and compares it to `keccak256(abi.encode(msg.sender, order.session))`: [3](#0-2) 

Because `commitment` is only used as a transient-storage slot key and is never checked to equal `keccak256(abi.encode(order))` inside `select()`, the wallet/solver-signing flow is structurally identical to the reported `experimental_requestSession` bug: a value that is supposed to attest to specific data (the order) is accepted and signed over/stored without validating that it actually maps to that data. A session key holder (the order owner) is expected to sign `(commitment, solver)` believing `commitment` represents their specific order, but nothing in `_select` enforces that binding — the enforcement is purely coincidental, relying on `fillOrder`'s independent recomputation matching whatever `commitment` was staged.

### Impact Explanation
If any caller (not necessarily the order owner) can obtain a session-key signature over an attacker-chosen `commitment` value — e.g., by convincing the session-key owner to sign a `SelectSolver(bytes32 commitment, address solver)` message without full context (analogous to a wallet blindly signing `sessionMerkleRoot` in the original report), or via a session key reused/derived across multiple orders — the signature can be replayed to stage an unauthorized solver selection for a *different* order's `commitment` slot in the same transient-storage namespace. Since `tstore`/`tload` slots are keyed only by the raw `commitment` value with no additional binding to the specific `Order` being filled at authorization time, this breaks the intended one-to-one link between a signed authorization and the order it was meant to protect, undermining the entire `solverSelection` access-control mechanism intended to prevent unauthorized fills of user-escrowed funds.

### Likelihood Explanation
Exploitability depends on how session-key signatures are solicited/displayed to the signer off-chain (not fully visible in this index), mirroring the original report's uncertainty about wallet-side merkle-root display. Given that `select()`/`_select()` is a public, permissionless entry point reachable by any solver/relayer submitting a transaction, and the on-chain code path performs zero verification that `commitment` corresponds to a real order, the root-cause defect (missing binding check) is concretely present regardless of off-chain mitigations.

### Recommendation
In `_select()` (or `select()`), require that `options.commitment` corresponds to an actual placed order — e.g., by requiring the full `Order` struct (or at minimum verifying `_orders[commitment]` has non-zero escrowed value, as `placeOrder` populates) as part of the call, and re-deriving `commitment = keccak256(abi.encode(order))` on-chain rather than trusting the caller-supplied value, exactly as `fillOrder` already does.

### Proof of Concept
1. `placeOrder` is called and stores escrow keyed by `commitment = keccak256(abi.encode(order))`: [4](#0-3) 
2. A solver calls `select(SelectOptions({commitment: arbitraryBytes32, solver: solverAddr, signature: sig}))` where `arbitraryBytes32` is not derived from any real `Order`, and `sig` is a session-key signature obtained without the signer confirming which order it binds to.
3. `_select` accepts this and stages `tstore(arbitraryBytes32, keccak256(abi.encode(solverAddr, sessionKey)))` with no check against any `Order`: [1](#0-0) 
4. If an attacker can cause `keccak256(abi.encode(order))` for a victim's real order to collide with, or be manipulated to equal, the staged `arbitraryBytes32` (e.g., through session-key reuse across orders, or a signer app that does not clearly bind the signed commitment to a specific order display), `fillOrder` for the victim's order will read the maliciously staged `tload` slot and authorize an unintended solver: [3](#0-2)

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

**File:** evm/src/apps/IntentGatewayV2.sol (L361-368)
```text
        commitment = keccak256(abi.encode(order));

        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;
```

**File:** evm/src/apps/IntentGatewayV2.sol (L443-451)
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
