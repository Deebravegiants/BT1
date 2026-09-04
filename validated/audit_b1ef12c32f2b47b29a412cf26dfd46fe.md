### Title
Arbitrary external call from `EmporiumUpgradeable` bypasses signature/authorization checks, enabling theft via unauthorized `approve`/`transferFrom` grants - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` lets a caller submit an arbitrary list of `EmporiumOperation` entries (`endpoint`, `callData`, `value`) that are executed with `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract's own address [1](#0-0) . When `stack.signerAddress == address(0)`, `verifyWallet` skips every authorization check (signature, deadline, max-fee) and only records the `emporiumMessage` nonce as used [2](#0-1) . This is the same bug class as the referenced `VoterProxy.vote` issue: a privileged contract that holds pooled funds performs an arbitrary, attacker-chosen external call, with the only guardrail being a check against two specific function selectors (`callHinkalWallet`, `doSendToRelay`) [3](#0-2) .

### Finding Description
`runAction` computes `balancesBefore`/`balancesAfter` and reconciles a balance-change equation only for `circomData.erc20TokenAddresses`, the token list *supplied by the caller for that specific proof* [4](#0-3) , [5](#0-4) . Nothing constrains `op.endpoint`/`op.callData` to only affect tokens in that array. In the "Stateless Interaction" branch (`signerAddress == address(0)`), the caller can set `op.endpoint` to the address of *any* ERC20 token the Emporium contract already holds a balance of (e.g., protocol/relay fee dust, or another user's token that hasn't been swept out yet), and `op.callData` to `approve(attacker, type(uint256).max)`. Because `approve` does not change the token balance, `balanceChange` for the token used in the proof (a different, unrelated token) stays consistent and the equation check at line 142 never fires. The attacker is left with unlimited `transferFrom` rights over the Emporium's holdings of that unrelated token, letting them later call `transferFrom(emporium, attacker, amount)` directly on the token contract — completely outside any Hinkal proof, nullifier, or signature check.

The root cause is identical to the report's root cause in `VoterProxy.vote`: an arbitrary-target, arbitrary-calldata external call gated only by a superficial selector blacklist, not a whitelist of allowed targets/actions, and only optionally protected by an EIP-712 signature that can be trivially bypassed by setting `signerAddress = address(0)`.

### Impact Explanation
This breaks the balance-conservation invariant the Emporium is built around: `balanceChange` is only tracked for tokens declared in the current proof's `erc20TokenAddresses`, but the arbitrary call can grant persistent, out-of-band transfer rights over *any* other token balance the contract holds (protocol/relay fees, dust from partially-completed multi-step operations, or funds in transit for other users). This is unauthorized asset movement/approval never sanctioned by any prover or signer, and it can be leveraged for outright theft of protocol/relay fees or of other users' funds sitting in the Emporium contract — matching the "theft or permanent freezing of protocol/relay fees" / "executing calls or moving assets ... never authorised" High-impact criteria.

### Likelihood Explanation
Any unprivileged actor able to generate a valid Hinkal proof for a trivial/self-owned note (the minimum requirement to call `_externalTransact` → `runAction` via `onlyAllowedRecipient`) can trigger this path. Setting `signerAddress = address(0)` is a normal, documented code path (not an edge case), so no privileged role, admin key, or relayer collusion is required.

### Recommendation
Whitelist the set of `endpoint` addresses (and/or function selectors) that `EmporiumOperation.ops` are permitted to call in the stateless branch, rather than only blacklisting the two wallet-callback selectors. Additionally, require the balance-change equation to detect any allowance/approval side effects, or forbid `approve`-style selectors entirely for tokens not explicitly authorized by the caller's signed message, and require `verifyWallet`'s signature check to be mandatory (not skippable via `signerAddress == address(0)`) whenever `ops` contains calls to ERC20 contracts.

### Proof of Concept
1. Emporium contract holds `TOKEN_X` balance (e.g., accumulated relay-fee dust from prior operations).
2. Attacker generates a minimal valid Hinkal proof involving only `TOKEN_Y` (their own shielded balance), calling `Hinkal._externalTransact` with `externalActionData.externalAddress = EmporiumUpgradeable`.
3. Attacker crafts `externalActionMetadata` decoding to an `EmporiumStack` with `signerAddress = address(0)` and `ops = [{ endpoint: TOKEN_X, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.approve, (attacker, type(uint256).max)) }]`.
4. `verifyWallet` returns immediately after marking the nonce used (no signature check) [6](#0-5) ; the loop executes `TOKEN_X.approve(attacker, max)` from the Emporium contract's address [7](#0-6) .
5. Since only `TOKEN_Y` balances are checked before/after, the transaction succeeds with `balanceChange` for `TOKEN_Y` unaffected.
6. Attacker separately calls `TOKEN_X.transferFrom(emporium, attacker, TOKEN_X.balanceOf(emporium))` to drain the Emporium's `TOKEN_X` holdings.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-144)
```text
        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        UTXO[] memory utxoSet = new UTXO[](
            circomData.erc20TokenAddresses.length
        );

        uint256 utxoSetLength;

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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-317)
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
