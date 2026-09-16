### Title
Solver-selection signature verification lacks EIP-1271 support, permanently blocking contract-wallet session keys from authorizing fills - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2`'s solver-selection flow authenticates the `SolverSelection` message purely via raw ECDSA recovery, with no `EIP-1271`/`isValidSignature` fallback for the `order.session` key. When a user places an order using a smart-contract wallet (Safe, MPC vault contract, etc.) as the session key, no signature that contract can ever produce will satisfy `ECDSA.recover`, so `select()` can never succeed for that order.

### Finding Description
`_select` recovers a signer address from the raw signature and treats it as the `sessionKey` to be checked against `order.session`: [1](#0-0) 

Nowhere in `IntentsBase.sol`, `ExtrinsicIntents.sol`, or `IntrinsicIntents.sol` is there a call to `IERC1271.isValidSignature` for this check — signature verification for solver selection is `ECDSA.recover`-only, unlike `SolverAccount`, which explicitly implements `isValidSignature` for its own EIP-7702-delegated EOA case: [2](#0-1) 

The `session` key is a user-supplied field at order placement (`order.session`), described in the documentation as "a disposable keypair that the user controls" — nothing in the contract enforces that this address must be an EOA: [3](#0-2) [4](#0-3) 

If a user (deliberately or via wallet-software default) sets `order.session` to a smart-contract wallet address, that contract cannot produce a raw ECDSA signature recoverable to its own address — only an `EIP-1271` `isValidSignature` response is possible for contract signers, per the EIP-1271 standard referenced in the original report. Because `_select` only accepts `ECDSA.recover(...) == order.session`, no valid authorization can ever be produced for that order, and `select()` (and therefore `fillOrder()`, which depends on the transient-storage authorization set by `select`) can never succeed for it.

This mirrors exactly the bug class from the external report: EIP-712/ECDSA-only signature verification excludes non-EOA signers, and the protocol's own selection mechanism assumes the session key is always an EOA even though it is user-chosen with no such restriction enforced on-chain.

### Impact Explanation
When `solverSelection` is enabled (the gateway's protection against unauthorized fills), an order whose `session` is a contract address becomes permanently unfillable through the intended selection path: no solver can ever be authorized to fill it, since the user can never produce a signature that passes `_select`'s `ECDSA.recover` check. The user's escrowed input assets are consequently starved of solver competition and cannot be delivered to the destination — the intent's designated "route" to deliver value is unusable for the entire class of users who set a non-EOA session key. Recovery is limited to whatever cancellation/expiry path exists (extra cost, delay, and reliance on cross-chain cancellation messaging), which does not restore the intended fill outcome and still requires additional user action outside the failed primary flow.

### Likelihood Explanation
Likelihood is moderate: any user is free to set `order.session` to any address they generate for the order, including a smart-contract wallet address (e.g., if their signing infrastructure or wallet defaults to a contract account, or a session key generated via an account-abstraction wallet). No validation rejects a contract address as `session` at order placement, so this can be triggered unintentionally by ordinary usage, not just adversarially.

### Recommendation
Extend `_select`'s signature check to fall back to `IERC1271.isValidSignature(digest, signature)` when `order.session.code.length > 0`, mirroring the pattern already used in `SolverAccount.isValidSignature`, e.g. via OpenZeppelin's `SignatureChecker.isValidSignatureNow`. This allows both EOA and contract-based session keys to authorize solver selection.

### Proof of Concept
1. User places an order via the intent gateway with `order.session = <SomeSafeMultisigAddress>` (a contract with no private key, and no `EIP-1271` support consulted by the protocol).
2. A solver submits a bid; the user attempts to authorize the winning solver by having the Safe produce an `EIP-1271` signature over the `SelectSolver` typed-data hash (`commitment`, `solver`).
3. `SolverAccount.validateUserOp` → `IntentGatewayV2.select` → `IntentsBase._select` executes:
   `address sessionKey = ECDSA.recover(digest, options.signature);`
   Since the Safe never produced a raw ECDSA signature (only an EIP-1271-compliant response is possible from a contract), `ECDSA.recover` either reverts (invalid signature length/components) or returns an unrelated address — never `order.session`.
4. The stored `selectionHash` therefore never matches, `fillOrder` never authorizes the solver, and the order can never be filled for as long as `order.session` remains a contract address — see `IntentsBase.sol` lines 560-572 above for the exact check that always fails in this scenario.

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

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L179-189)
```text
    /**
     * @notice ERC-1271 signature validation for EIP-7702 delegated accounts.
     * @dev Required so that protocols using OpenZeppelin's SignatureChecker (e.g. USDC's
     *      EIP-2612 permit) can verify signatures from this account. Under EIP-7702 the
     *      account has code, so SignatureChecker takes the ERC-1271 path instead of
     *      ecrecover. Delegates to {_rawSignatureValidation} which performs ECDSA recovery
     *      and checks that the recovered address equals address(this) (the delegating EOA).
     */
    function isValidSignature(bytes32 hash, bytes calldata signature) external view override returns (bytes4) {
        return _rawSignatureValidation(hash, signature) ? bytes4(0x1626ba7e) : bytes4(0xffffffff);
    }
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L126-132)
```text
<Step>
### Order placement
The user places an order with `order.session` set to the session key's public address. The session key is a disposable keypair that the user controls.
</Step>
<Step>
### Auction
Solvers observe the `OrderPlaced` event and compete by posting UserOperations to hyperbridge that specify the output amounts they'll provide. A bid is bound to its order structurally: the UserOperation's ERC-4337 nonce key (the upper 192 bits of the nonce) must equal the lower 192 bits of `keccak256(commitment ‖ session)` — binding both the order and the session key the solver is bidding against — and its calldata carries the `fillOrder` call for that order. The solver then signs the operation as EntryPoint v0.8 EIP-712 typed data (domain `ERC4337`/`1`, type `PackedUserOperation`) — the digest of which *is* the `userOpHash` — so the signed payload remains fully inspectable by the solver's signing infrastructure (hardware wallets, MPC or TEE policy engines) rather than an opaque digest.
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L134-143)
```text
<Step>
### Bid selection
The user reviews all bids and picks the best one. To authorize the winning solver, the user signs an EIP-712 `SolverSelection` message with the session key:
```solidity
struct SolverSelection {
    bytes32 commitment,   // order commitment hash
    address solver       // authorized solver address
}
```
The session signature is appended to the solver's `UserOperation` as `abi.encodePacked(commitment, solverSignature, sessionSignature)` and submitted to an ERC-4337 bundler. The solver pays all gas costs for on-chain execution.
```
