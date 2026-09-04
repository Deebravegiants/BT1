### Title
Unaccounted ETH drain via `EmporiumOperation.value` on stateless ops bypasses balance reconciliation - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` only reconciles balances for tokens present in `circomData.erc20TokenAddresses`, but `op.value` (native ETH forwarded via `op.endpoint.call{value: op.value}(op.callData)`) is spent unconditionally for every op regardless of whether `address(0)` is in that array. An attacker can craft a circomData/EmporiumStack where `address(0)` is excluded from `erc20TokenAddresses`, letting them siphon any ETH balance sitting in `EmporiumUpgradeable` (from dust/leftovers of other users' swaps, or direct sends to its `receive()`) to an attacker-controlled endpoint with no accounting check and, when `stack.signerAddress == address(0)`, no signature requirement at all.

### Finding Description
Equality broken (Value Conservation): the change in `EmporiumUpgradeable`'s ETH balance should equal `sum(deltaAmountChanges[i] where erc20TokenAddresses[i] == address(0))`. This only holds if `address(0)` is included in `circomData.erc20TokenAddresses`.

Code path:
- `runAction` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-160`) decodes the attacker-supplied `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` and iterates `stack.ops`.
- For CASE 2 ("Stateless Interaction"), `op.endpoint.call{value: op.value}(op.callData)` is executed unconditionally [1](#0-0) . This send happens regardless of whether `address(0)` appears anywhere in `circomData.erc20TokenAddresses`.
- The post-op reconciliation loop only walks `circomData.erc20TokenAddresses` [2](#0-1) ; if the attacker omits `address(0)` from that array, the ETH balance decrease from `op.value` is never diffed against `balancesBefore`/`balancesAfter`, and `handleOut` never even considers index for ETH, so `BalanceChangeShouldBePositive` cannot trigger.
- `verifyWallet` only checks a signature if `stack.signerAddress != address(0)` [3](#0-2) ; setting `signerAddress = address(0)` bypasses signature verification entirely for the ops list, meaning the attacker (who fully controls their own `circomData`/proof per the threat model) needs no third-party authorization to set an arbitrary `op.endpoint`/`op.value`/`op.callData`.
- `dimensionsCheck`/`performHinkalChecks` (`contracts/HinkalHelper.sol:64-236`) enforce only structural/length equalities between `erc20TokenAddresses`, `amountChanges`, `onChainCreation`, nullifiers, and commitments; there is no requirement that `address(0)` be present, nor any constraint linking `op.value` inside `externalActionMetadata` to `amountChanges`. The circuit's `inTotal + amountChanges === outTotal` constraint likewise never sees `op.value` because it operates only on the declared `erc20TokenAddresses`/`amountChanges` vectors.
- `EmporiumUpgradeable` also has `receive() external payable {}` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:369`), so it can and does accumulate standing ETH (e.g., refunds/dust from other users' unrelated stack operations that didn't include `address(0)` in their token list, or direct sends).

Attacker's exact call: submit a normal Hinkal transact (with a valid proof over the attacker's own nullifiers/UTXOs — precondition satisfied since attacker is a legitimate depositor) targeting the Emporium external action, with `circomData.erc20TokenAddresses` excluding `address(0)`, and `externalActionData.externalActionMetadata` encoding an `EmporiumStack` with `signerAddress = address(0)` and a single stateless `EmporiumOperation{ endpoint: attackerContract, invokeWallet: false, value: <current ETH balance of Emporium>, callData: <anything that doesn't match the two guarded selectors> }`.

Exploit flow: Emporium forwards `op.value` ETH to the attacker's endpoint via `call`; the reconciliation loop skips ETH entirely because it isn't in `erc20TokenAddresses`; no revert occurs; the attacker's other legitimate token operations (if any) proceed and mint their own UTXO(s) normally. Net effect: ETH belonging to the Emporium contract (accumulated from other users' unrelated interactions) is transferred to the attacker with zero on-chain accounting of the loss.

Why existing guards fail: `onlyAllowedRecipient` only restricts who can call `runAction` (the main Hinkal contract), not what the decoded `EmporiumStack` can contain; `verifyWallet`'s signature check is opt-in (skipped when `signerAddress == address(0)`); `dimensionsCheck`/`checkOnchainCreation` never require `address(0)` inclusion or constrain `op.value`; the balance-diff loop in `runAction` is scoped strictly to the attacker-chosen `erc20TokenAddresses` array.

### Impact Explanation
Direct theft of ETH held by `EmporiumUpgradeable` that originated from other users' unrelated transactions/deposits (dust, refunds, or stray transfers via `receive()`), executed without their authorization and without triggering any revert or balance-conservation check. This is repeatable on every transaction as long as residual ETH exists in the contract, and it can be combined with the attacker's own legitimate token flows in the same tx to also mint a UTXO for pulled tokens. This matches Critical severity ("direct theft of shielded or in-flight user funds" / theft of protocol-held funds belonging to other users).

### Likelihood Explanation
Preconditions: (1) `EmporiumUpgradeable` must hold nonzero ETH balance not currently accounted for by any in-flight `erc20TokenAddresses` array (achievable via `receive()` or via dust left from other users' stateless ops that didn't declare `address(0)`); (2) attacker must be able to submit a normal transact call with a valid proof for their own funds, and freely construct `externalActionMetadata` — both permitted under the stated threat model since the attacker controls every field of `CircomData` and the `EmporiumStack` is not proof-constrained beyond hash consistency they control themselves. Attacker cost is a single transaction; the attack is fully repeatable each time residual ETH reappears.

### Recommendation
Enforce value conservation for native ETH exactly as for ERC20 tokens: either (a) require `address(0)` to always be present in `circomData.erc20TokenAddresses` whenever any `op.value > 0` in the decoded `EmporiumStack`, and include it in the `balancesBefore`/`balancesAfter` diff, or (b) track a running `nativeValueBudget` (sum of `op.value` across all ops) at the start of `runAction` and require it be fully backed by a corresponding negative `deltaAmountChanges` entry for `address(0)`, reverting otherwise. Additionally, disallow `signerAddress == address(0)` from skipping signature verification when `op.value > 0` on stateless ops, or require an explicit ETH accounting invariant independent of `erc20TokenAddresses` selection.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as allowed external action), and a minimal attacker-controlled `receive()`-only contract `Sink`.
2. Fund `EmporiumUpgradeable` with ETH from a legitimate, unrelated flow (e.g., simulate a prior stateless op from user A whose `erc20TokenAddresses` excluded `address(0)` but whose op refunded ETH to Emporium, or simply `vm.deal(address(emporium), 1 ether)` to represent accumulated dust).
3. As the attacker, build `CircomData` with `erc20TokenAddresses = [attackerToken]` (excludes `address(0)`), `amountChanges` reflecting only `attackerToken`, `externalActionData.externalActionMetadata` = ABI-encoded `EmporiumStack{ signerAddress: address(0), ops: [EmporiumOperation{endpoint: address(sink), invokeWallet: false, value: 1 ether, callData: ""}] }`, generate a valid proof/nullifiers for the attacker's own UTXO(s) for `attackerToken`.
4. Call Hinkal's transact function with this `circomData`.
5. Assert: `address(sink).balance == 1 ether` after the call (theft occurred); assert `balancesBefore`/`balancesAfter` diff array recorded in `runAction` for `erc20TokenAddresses` (attackerToken only) shows no entry accounting for the 1 ETH loss; assert the call does NOT revert with `BalanceChangeShouldBePositive`, proving the ETH decrease was never checked against any `deltaAmountChanges` entry for `address(0)`.

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-151)
```text
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 balanceChange = int256(balancesAfter[i]) -
                int256(balancesBefore[i]);

            if (deltaAmountChanges[i] < 0) {
                balanceChange -= deltaAmountChanges[i];
                // this equation reads: total change of emporium balance = what was moved to emporium (-deltaAmountChange) + how emporium balance changed through tx (balanceChange)
            }

            // the only case when balanceChange can be < 0, when there were some funds on emporium before the call
            if (balanceChange < 0) {
                revert BalanceChangeShouldBePositive();
            }

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
            }
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-316)
```text
    function verifyWallet(
        EmporiumStack memory stack,
        CircomData calldata circomData
    ) internal {
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }
```
