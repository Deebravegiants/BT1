### Title
Hardcoded `fillOrder` selector in `SolverAccount._containsFillOrder` does not match the actual deployed `IntentGatewayV2` signature on chains still running the pre-`validUntil` gateway - ([File: evm/src/apps/intentsv2/SolverAccount.sol])

### Summary
`SolverAccount.sol` hardcodes `FILL_ORDER_SELECTOR = IIntentGatewayV2.fillOrder.selector`, resolved against the *current* `IIntentGatewayV2` interface in `@hyperbridge/core/apps/IntentGatewayV2.sol`, whose `fillOrder(Order, FillOptions)` includes the `validUntil` field added on 2026-08-27. Adding that field changed the function selector from `0x5cfb1ea5` (v1) to `0xa5470064` (v2), and the codebase's own SDK docs confirm both shapes are simultaneously live on-chain across chains (`sdk/packages/sdk/src/protocols/intents/fillOrderCodec.ts`, `LEGACY_FILL_OPTIONS_IMPLEMENTATIONS`, `CHAINS_WITHOUT_VALID_UNTIL`). `SolverAccount` is compiled once against the v2 selector regardless of which `fillOrder` signature the `IntentGatewayV2` deployment at its immutable `INTENT_GATEWAY_V2` address actually exposes, exactly mirroring the M-7 pattern where `UniV3Controller` hardcoded selectors that didn't match the actually-deployed Router.

### Finding Description
`SolverAccount.validateUserOp` fast-paths standard 65-byte ECDSA signatures through `super.validateUserOp`, but only after `_containsFillOrder` confirms the batched calldata does not target `INTENT_GATEWAY_V2.fillOrder`: [1](#0-0) 

The selector used for that scan is fixed at compile time from the current interface: [2](#0-1) 

and the scan itself only matches calls whose 4-byte selector equals that constant: [3](#0-2) 

The SDK's own `fillOrderCodec.ts` documents that `fillOrder` exists in two functionally different, differently-selectored shapes, and that both are concurrently deployed across chains until every gateway is upgraded: [4](#0-3) [5](#0-4) 

On any chain whose `IntentGatewayV2` is still running the pre-`validUntil` (v1) implementation, the real `fillOrder` selector at `INTENT_GATEWAY_V2` is `0x5cfb1ea5`, not the hardcoded `FILL_ORDER_SELECTOR` (`0xa5470064`) baked into `SolverAccount`. `_containsFillOrder` therefore never recognizes a genuine `fillOrder` call in that scenario — the exact function-signature mismatch pattern from M-7, where a controller's hardcoded selectors didn't match the router actually deployed at the configured address.

### Impact Explanation
The check exists specifically to stop the griefing attack the code comments describe: bids are public and carry a valid 65-byte solver ECDSA signature over the plain `userOpHash`; anyone can strip the commitment/session signature and resubmit the bid through the standard-ECDSA fast path. Without `_containsFillOrder` catching it, the op executes `fillOrder` without a `select()` staged in the same validation, the fill reverts, but the userOp's nonce is consumed and the solver's `SolverAccount` is charged gas (`_payPrefund` / bundler prefund) for a submission it never authorized as a fast-path op — as the code's own docstring states: "the bid's nonce would be consumed and the solver griefed of the gas fees." On any chain still running the pre-`validUntil` gateway, this exact protection silently does nothing, exposing every solver on that chain to unpriced, front-runnable gas griefing and nonce burn triggered by any unprivileged party replaying public bid calldata — this is an unauthorized action forced on the solver's account and a concrete loss of solver funds, reachable by any actor and requiring no privilege.

### Likelihood Explanation
High on any chain where the `IntentGatewayV2` deployment has not yet been upgraded past the pre-`validUntil` implementation — the SDK explicitly tracks such chains today (`LEGACY_FILL_OPTIONS_IMPLEMENTATIONS`, `CHAINS_WITHOUT_VALID_UNTIL`), confirming this is not a hypothetical future state but a currently-live condition across the deployment fleet. The bid calldata needed to trigger it is public by design (embedded solver signature over `userOpHash`), so any observer can replay it with zero cost beyond gas, matching the trivially reachable exploit path in the original M-7 report.

### Recommendation
Do not resolve `FILL_ORDER_SELECTOR` from a single hardcoded interface constant. Either:
1. Recognize both `fillOrder` selectors (v1 `0x5cfb1ea5` and v2 `0xa5470064`) in `_containsFillOrder`, or
2. Detect the actual `fillOrder` selector deployed at `INTENT_GATEWAY_V2` (e.g., by resolving its ERC-1967 implementation and matching against the known legacy-implementation set, as `fillOrderCodec.ts` already does off-chain) and gate on the correct one per deployment.

### Proof of Concept
1. Deploy `SolverAccount` pointing `INTENT_GATEWAY_V2` at a chain whose gateway is still the pre-`validUntil` implementation (address `0x976b268b06f545c4a2bf44866aa2465bd8b3c67d` per `LEGACY_FILL_OPTIONS_IMPLEMENTATIONS`), so the real on-chain `fillOrder` selector is `0x5cfb1ea5`.
2. Observe a public solver bid: a `PackedUserOperation` with a 65-byte ECDSA signature over `userOpHash`, whose `callData` is an ERC-7821 `execute` batch containing a call to `INTENT_GATEWAY_V2.fillOrder(...)` encoded with the v1 selector `0x5cfb1ea5`.
3. Strip nothing (the signature is already 65 bytes) and resubmit the op through the bundler/EntryPoint.
4. `_containsFillOrder` computes `bytes4(calls[i].callData)` = `0x5cfb1ea5`, which never equals the hardcoded `FILL_ORDER_SELECTOR` (`0xa5470064`), so `_containsFillOrder` returns `false`.
5. `validateUserOp` proceeds via `super.validateUserOp` (the standard-ECDSA fast path succeeds since the signature is valid), consuming the account's nonce and charging `missingAccountFunds`/prefund; execution of `fillOrder` on-chain then reverts for lack of a staged `select()`, leaving the solver's `SolverAccount` griefed of gas and with a burned nonce — reproducing exactly the scenario the docstring in `evm/src/apps/intentsv2/SolverAccount.sol:80-88` says this check exists to prevent, on the class of deployments the SDK itself still tracks as legacy.

### Citations

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L47-55)
```text
    /**
     * @notice Cached select function selector
     */
    bytes4 private constant SELECT_SELECTOR = IIntentGatewayV2.select.selector;

    /**
     * @notice Cached fillOrder function selector
     */
    bytes4 private constant FILL_ORDER_SELECTOR = IIntentGatewayV2.fillOrder.selector;
```

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L103-112)
```text
    function validateUserOp(PackedUserOperation calldata op, bytes32 userOpHash, uint256 missingAccountFunds)
        public
        override
        onlyEntryPoint
        returns (uint256)
    {
        if (op.signature.length == ECDSA_SIGNATURE_LENGTH) {
            if (_containsFillOrder(op.callData)) return ERC4337Utils.SIG_VALIDATION_FAILED;
            return super.validateUserOp(op, userOpHash, missingAccountFunds);
        }
```

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L152-163)
```text
    function _containsFillOrder(bytes calldata callData) private view returns (bool) {
        if (callData.length < 4 || bytes4(callData[0:4]) != EXECUTE_SELECTOR) return false;

        (, bytes memory executionData) = abi.decode(callData[4:], (bytes32, bytes));
        Execution[] memory calls = abi.decode(executionData, (Execution[]));

        for (uint256 i = 0; i < calls.length; i++) {
            bool hasFillOrder = calls[i].target == INTENT_GATEWAY_V2 && bytes4(calls[i].callData) == FILL_ORDER_SELECTOR;
            if (hasFillOrder) return true;
        }
        return false;
    }
```

**File:** sdk/packages/sdk/src/protocols/intents/fillOrderCodec.ts (L1-14)
```typescript
import { encodeFunctionData, decodeFunctionData, type PublicClient } from "viem"
import { ABI as IntentGatewayV2ABI } from "@/abis/IntentGatewayV2"
import type { FillOptions, HexString, Order } from "@/types"

/**
 * `FillOptions` gained a `validUntil` field. Adding a field to a struct changes the
 * enclosing function's selector, so `fillOrder` has two incompatible shapes in the wild:
 *
 *   v1  fillOrder(Order, (uint256 relayerFee, uint256 nativeDispatchFee, TokenInfo[] outputs))
 *   v2  fillOrder(Order, (uint256 relayerFee, uint256 nativeDispatchFee, uint256 validUntil, TokenInfo[] outputs))
 *
 * The selectors differ (`0x5cfb1ea5` vs `0xa5470064`), so a v2 payload sent to a v1
 * deployment finds no matching function and reverts rather than mis-decoding — which is the
 * safe failure, but it does mean callers have to know which shape a gateway speaks.
```

**File:** sdk/packages/sdk/src/protocols/intents/fillOrderCodec.ts (L63-92)
```typescript
/**
 * IntentGateway implementations deployed before `FillOptions.validUntil` existed.
 *
 * The list is of *legacy* implementations rather than current ones, so the default is v2 and
 * nothing has to be added here when a new implementation ships — only when an old one is
 * discovered. Once every deployment is upgraded this set is vestigial and still correct.
 *
 * The alternative, listing known-good implementations, would be the version constant this
 * replaced wearing a different hat: a value someone must remember to update on every upgrade,
 * where forgetting breaks every fill on the chain.
 */
export const LEGACY_FILL_OPTIONS_IMPLEMENTATIONS = new Set<string>([
	// The pre-validUntil IntentGatewayV2 implementation. One entry covers every chain: the
	// protocol contracts are CREATE2-deployed, so this is the implementation address on all
	// of them (confirmed with the maintainers).
	"0x976b268b06f545c4a2bf44866aa2465bd8b3c67d",
])

/**
 * Chains whose IntentGateway has not been redeployed with `FillOptions.validUntil` yet.
 *
 * A blunter instrument than {@link LEGACY_FILL_OPTIONS_IMPLEMENTATIONS} and used for the same
 * reason: those chains run a pre-`validUntil` implementation whose address is not tracked here,
 * so the address check would wrongly read them as current and every fill would revert on a
 * selector that does not exist.
 *
 * Delete a chain from this set when its gateway is redeployed. Once the set is empty the
 * implementation-address check covers everything on its own.
 */
export const CHAINS_WITHOUT_VALID_UNTIL = new Set<number>([
```
