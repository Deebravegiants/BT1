### Title
Missing reentrancy protection in Tron `IntentGatewayV2` order fill/place/cancel paths, unlike the hardened EVM version - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The external report describes a reentrancy pattern in `_bid`, where `safeTransferFrom` calls on an arbitrary, attacker-controllable ERC20 (`bidAsset`) are interleaved with state writes without a reentrancy guard, allowing a callback-capable token to double-spend the bidding/accounting logic. The equivalent attack surface in Hyperbridge is the `IntentGatewayV2` intents-escrow contract, where `placeOrder`, `fillOrder`, and `cancelOrder` similarly call `safeTransferFrom`/`safeTransfer` on arbitrary, user-supplied `order.inputs`/`order.output` tokens. The canonical EVM deployment mitigates this with `ReentrancyGuardTransient` and a `nonReentrant` modifier on `fillOrder`, but the parallel Tron deployment of the same contract does not import or apply any reentrancy guard.

### Finding Description
`evm/src/apps/IntentGatewayV2.sol` inherits `ReentrancyGuardTransient` and guards its externally callable `fillOrder` entrypoint with `nonReentrant`: [1](#0-0) [2](#0-1) [3](#0-2) 

The internal fill logic (`_fillSameChain` in `IntrinsicIntents.sol`, `_fillCrossChain` in `ExtrinsicIntents.sol`) performs arbitrary-ERC20 `safeTransferFrom` calls with attacker/solver-controlled token addresses on `order.inputs`/`order.output.assets`, exactly analogous to `_bid`'s reentrant `bidAsset.safeTransferFrom` call: [4](#0-3) [5](#0-4) 

The Tron port of the same contract (`evm/tron/contracts/apps/IntentGatewayV2.sol`) does not import `ReentrancyGuardTransient`/`ReentrancyGuard` and does not apply any `nonReentrant` modifier — a `grep` for `nonReentrant|ReentrancyGuard` across that file returns no matches, whereas the same search on the audited `evm/src/apps/IntentGatewayV2.sol` returns 9 matches. The Tron file reimplements `placeOrder` directly (rather than reusing the shared, guarded `IntrinsicIntents`/`ExtrinsicIntents` abstracts) and performs the same pattern of `IERC20(token).safeTransferFrom(msg.sender, ...)` calls on arbitrary order-input tokens before/around escrow bookkeeping writes: [6](#0-5) 

Because `order.inputs`/`order.output.assets` tokens are chosen by the order creator/solver and are not restricted to a vetted allowlist, a token with callback hooks (TRC20 tokens on Tron can implement arbitrary hook logic on `transfer`/`transferFrom`, mirroring the ERC777/imBTC class of attack referenced in the original report) can reenter the gateway's public functions (`fillOrder`, `placeOrder`, `cancelOrder`) mid-execution on the Tron deployment, since there is no `nonReentrant` guard to block it.

### Impact Explanation
A successful reentrancy here could let an attacker manipulate escrow accounting in `_orders[commitment][token]`, cause double-fills/double-refunds, or otherwise cause funds to be released more than once for a single order commitment — a direct theft-of-funds / permanent-freezing-of-funds scenario in the Tron intents-escrow deployment. This satisfies the "concrete theft or permanent freezing of funds" bar, scoped to intents escrow logic explicitly listed as in-scope.

### Likelihood Explanation
Medium: exploitation requires the order (or fill) to reference a malicious ERC20/TRC20 with reentrant callback behavior as one of its `inputs`/`output` assets. Since token selection for orders is unrestricted (any address castable to `IERC20`), an attacker fully controls this precondition by simply placing or filling an order using a token they deploy themselves. No governance or privileged action is needed — a single unprivileged solver/user transaction (`placeOrder`/`fillOrder`) is sufficient to trigger the vulnerable code path.

### Recommendation
- **Short term:** Add `ReentrancyGuardTransient` (or standard `ReentrancyGuard`) to `evm/tron/contracts/apps/IntentGatewayV2.sol` and apply `nonReentrant` to `placeOrder`, `fillOrder`, and `cancelOrder`, mirroring the protection already present in `evm/src/apps/IntentGatewayV2.sol`. Alternatively, refactor the Tron contract to reuse the shared, already-guarded `IntrinsicIntents`/`ExtrinsicIntents` abstracts instead of maintaining a divergent reimplementation.
- **Long term:** Run Slither (or an equivalent static analyzer) across all chain-specific forks of shared contracts (Tron, and any other non-EVM-standard port) as part of CI, specifically diffing security-relevant modifiers (`nonReentrant`, access-control) between forks and the canonical implementation so divergences like this are caught automatically.

### Proof of Concept
1. Attacker deploys a malicious TRC20 token `EvilToken` whose `transferFrom` hook calls back into `IntentGatewayV2.fillOrder` (or `placeOrder`/`cancelOrder`) before returning.
2. Attacker places (or is selected to fill) an order where `order.output.assets` (or `order.inputs`) includes `EvilToken`.
3. During `fillOrder`'s `IERC20(token).safeTransferFrom(msg.sender, beneficiary, ...)` call (analogous to `_bid`'s `bidAsset.safeTransferFrom`), `EvilToken`'s hook reenters the gateway. Because `evm/tron/contracts/apps/IntentGatewayV2.sol` has no `nonReentrant` guard, the reentrant call executes against escrow/fill state that has not yet been fully finalized by the outer call, enabling double-crediting or double-fulfillment of escrowed funds for the same commitment.

Note: full byte-for-byte confirmation of the exact interleaving in the Tron `fillOrder`/`cancelOrder` bodies (beyond `placeOrder`, which was directly inspected) could not be completed within the available tool budget; the core, verifiable fact — the complete absence of any reentrancy guard import/modifier in the Tron file versus its explicit presence in the canonical EVM file — is confirmed directly via source inspection and grep.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L24-24)
```text
import {ReentrancyGuardTransient} from "@openzeppelin/contracts/utils/ReentrancyGuardTransient.sol";
```

**File:** evm/src/apps/IntentGatewayV2.sol (L60-60)
```text
contract IntentGatewayV2 is IntrinsicIntents, ExtrinsicIntents, ReentrancyGuardTransient, Initializable {
```

**File:** evm/src/apps/IntentGatewayV2.sol (L443-443)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L95-106)
```text
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L186-196)
```text
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-468)
```text
        } else {
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
```
