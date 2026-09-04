### Title
Emporium stateless op can invoke another action's `runAction` with a forged, unverified `CircomData`, bypassing `performHinkalChecks`/`verifyProof` and enabling arbitrary `transferFrom` - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction`'s "stateless interaction" branch executes an arbitrary `op.endpoint.call(op.callData)` where both `endpoint` and `callData` are fully attacker-controlled bytes taken from `circomData.externalActionData.externalActionMetadata`. If any other `ExternalActionBaseV2`/`ExternalActionBaseUpgradeable` action lists Emporium's address in its `isAllowedRecipient`/`_isAllowedRecipient` map, the attacker can encode a call to that action's `runAction(CircomData, int256[])` with a completely forged `CircomData` struct that never passed through `Hinkal.transact`'s `performHinkalChecks`, `verifyProof`, or `rootHashExists` checks.

### Finding Description
The equality that should hold end-to-end is: every `CircomData` struct consumed by an action's `runAction` must be the same struct that was verified by `HinkalHelper.performHinkalChecks` (which pins `circomData.originalSender == sender` or `address(0)` for relay flows, per [1](#0-0) ) and matched against `circomData.calldataHash`/`verifyProof`.

That equality holds for the *outer* call: `Hinkal.transact` calls `hinkalHelper.performHinkalChecks(...)` then `verifyProof(...)` before dispatching to `_externalTransact` → `IExternalActionV2(...).runAction(circomData, deltaAmountChanges)` [2](#0-1) .

It is broken for any *nested* call reachable from `EmporiumUpgradeable.runAction`'s stateless branch: [3](#0-2) 
Here `op.endpoint` and `op.callData` come straight out of `abi.decode(circomData.externalActionData.externalActionMetadata, (EmporiumStack))` [4](#0-3) , which is attacker-authored bytes only constrained by a self-computed hash (`calldataHash`), never semantically validated by the circuit or by `performHinkalChecks`.

`onlyAllowedRecipient` only checks `msg.sender` against a mapping keyed by address [5](#0-4)  / [6](#0-5)  — it does not, and cannot, verify that the `CircomData` argument being passed in was ever checked by `Hinkal.transact`. If Emporium's address happens to be present in another action's allow-list (e.g. `DepositOnChainUtxosExternalAction`), the attacker can set `op.callData = abi.encodeWithSelector(runAction.selector, forgedCircomData, forgedDeltaAmounts)` with `op.endpoint = <that action>`.

`DepositOnChainUtxosExternalAction.runAction` then executes with a completely forged struct: it reads `userAddress = circomData.originalSender` (attacker-chosen, unchecked against any signer/proof since this path never went through `performHinkalChecks`) and calls [7](#0-6)  `transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal)`, where `msg.sender` is Emporium's address (since Emporium is the direct caller of the nested `runAction`). This succeeds against any ERC20 token for which `userAddress` (attacker's chosen victim) has an outstanding allowance to Emporium's address — an allowance that may exist from normal Hinkal usage patterns where users approve action/router contracts to pull tokens.

Existing guards fail because: `performHinkalChecks`, `verifyProof`, `rootHashExists`, and the calldata-hash/circuit constraints are all applied only to the top-level `circomData` passed into `Hinkal.transact`; they have no visibility into, and are not re-invoked for, the second, forged `CircomData` synthesized inside Emporium's raw `.call`. `onlyAllowedRecipient` is a coarse, address-only gate that was designed to restrict which contracts may call an action (documented as being "used to handle VolatileTokenAction and Hinkal interactions"), not to certify that the calldata being forwarded originated from a verified proof.

### Impact Explanation
This allows an unprivileged attacker to trigger `transferERC20TokenFrom`/`transfer` calls with an arbitrary `from` address (any address that has approved the intermediate action contract), moving that victim's tokens into the attacker's control path (Emporium's balance, from which the attacker's own outer transaction subsequently withdraws via `handleOut`/UTXO creation under their own stealth address). This is direct theft of user funds authorized by neither the wallet owner nor any Groth16 proof — matching the **Critical** category ("direct theft of shielded or in-flight user funds," "executing calls or moving assets a wallet owner or prover never authorised"). It is repeatable per victim allowance and per discoverable allow-listed action pair.

### Likelihood Explanation
Exploitability strictly depends on a precondition the attacker cannot set but only needs to discover: two deployed actions where one (reachable as an `op.endpoint` from Emporium's stateless branch, i.e. typically Emporium itself) is present in the other's `isAllowedRecipient`/`_isAllowedRecipient` map, discoverable via the public `isAllowedRecipient(address)` getter or a direct storage read at `ExternalActionBaseLocation`. It further requires that some account has an outstanding ERC20 allowance to that intermediate action's address (a realistic condition in a pull-based deposit protocol like this one). Deployment/configuration scripts that set `_allowedRecipients` were not found in the indexed portion of the repo, so I could not confirm from this index whether such an overlapping configuration currently exists on any live deployment — this should be verified directly against deployment artifacts/on-chain state before treating it as confirmed-exploitable in production, but the code path itself is a genuine architectural flaw independent of whether it is currently configured.

### Recommendation
- Never route unauthenticated, attacker-supplied `CircomData` into another action's `runAction` via a raw low-level `.call`. `EmporiumUpgradeable`'s stateless branch should restrict `op.endpoint` to a strict allowlist of external protocol routers/tokens (not other Hinkal action contracts), or explicitly block calls whose selector matches any `IExternalActionV2.runAction` (similar to the existing `IHinkalWallet` selector blocklist at [8](#0-7) ).
- Have every action's `runAction` re-derive/re-verify that its `CircomData` originated from the currently executing, checked `Hinkal.transact` context (e.g., by having `Hinkal`/`HinkalHelper` pass a verified marker or by having actions callable only through `Hinkal`'s dispatch, never transitively through another action).
- Treat `isAllowedRecipient` membership as a capability that should never include another action contract's address unless that action independently re-validates all fields of any `CircomData` it receives.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (proxy), and `DepositOnChainUtxosExternalAction`, configuring `DepositOnChainUtxosExternalAction`'s `_allowedRecipients` to include Emporium's address (the owner-configured precondition), and register both as external actions on `Hinkal`.
2. Deploy an ERC20 token; have a "victim" account approve `EmporiumUpgradeable`'s address for `1000e18` tokens (simulating a normal deposit-approval flow) but never call `Hinkal.transact` themselves.
3. As the attacker, craft `deltaAmounts=[0]` and forged `CircomData` with `originalSender = victim`, `erc20TokenAddresses = [token]`, and `externalActionData.externalActionMetadata` encoding `utxoAmounts` totalling `1000e18`; ABI-encode a call to `DepositOnChainUtxosExternalAction.runAction(forgedCircomData, [0])`.
4. Build an outer, legitimately-proved `CircomData`/proof for `Hinkal.transact` targeting Emporium's `externalActionId`, with `externalActionMetadata` = `EmporiumStack{ ops: [{endpoint: depositAction, invokeWallet: false, value: 0, callData: <step 3 bytes>}], signerAddress: address(0) }`.
5. Call `Hinkal.transact(...)` as the attacker.
6. Assert: (a) before/after — `token.allowance(victim, emporium)` drops and `token.balanceOf(victim)` decreases by `1000e18` despite `victim` never having called `Hinkal.transact` or signed any proof in this transaction; (b) `circomData.originalSender` used inside the nested `runAction` (`victim`) differs from `msg.sender`/`tx.origin` of the outer `Hinkal.transact` call (the attacker), demonstrating the broken authority equality.

### Citations

**File:** contracts/HinkalHelper.sol (L213-219)
```text
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );
```

**File:** contracts/Hinkal.sol (L234-261)
```text
    function _externalTransact(
        CircomData calldata circomData
    ) internal returns (UTXO[] memory) {
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );

        int256[] memory deltaAmountChanges = new int256[](
            circomData.erc20TokenAddresses.length
        );
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            deltaAmountChanges[i] = _calculateDeltaAmount(circomData, i);
            if (deltaAmountChanges[i] < 0) {
                transferERC20TokenOrETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    uint256(-deltaAmountChanges[i])
                );
            }
        }

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L80-83)
```text
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-113)
```text
            // CASE 2: Stateless Interaction
            else {
                bytes4 selector = bytes4(op.callData);
                if (
                    selector == IHinkalWallet.callHinkalWallet.selector ||
                    selector == IHinkalWallet.doSendToRelay.selector
                ) {
                    revert UnauthorizedWalletCall();
                }

                (success, err) = op.endpoint.call{value: op.value}(op.callData);
            }
```

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L16-22)
```text
    modifier onlyAllowedRecipient() {
        require(
            isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L39-46)
```text
    modifier onlyAllowedRecipient() {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();
        require(
            $._isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L75-82)
```text
            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
```
