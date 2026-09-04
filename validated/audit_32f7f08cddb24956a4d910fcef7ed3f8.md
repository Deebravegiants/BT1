### Title
Unauthenticated arbitrary-call forwarder in `EmporiumUpgradeable.runAction` drains any pre-granted ERC20 allowance to the Emporium contract - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` executes a list of attacker-supplied `EmporiumOperation`s (`endpoint`, `callData`, `value`) directly from the Emporium contract's own address whenever `stack.signerAddress == address(0)`. In that case `verifyWallet` returns immediately without any signature check, so the operations are completely unauthenticated. Only two hard-coded selectors (`callHinkalWallet`, `doSendToRelay`) are blocked; an ERC20 `transferFrom` targeting any third party who has ever granted an allowance to the Emporium contract is not blocked, letting an unprivileged Hinkal user drain that allowance and mint themselves a legitimate shielded UTXO with the proceeds.

### Finding Description
`runAction` decodes the `EmporiumStack` purely from `circomData.externalActionData.externalActionMetadata`, which is chosen by whoever submits the `transact()` call: [1](#0-0) 

`verifyWallet` skips all signature/EIP-712 verification when `stack.signerAddress == address(0)` — it only marks the message as used and returns: [2](#0-1) 

For each op, when `invokeWallet` is false (or `signerAddress` is zero), execution falls into "CASE 2: Stateless Interaction", which performs a raw low-level call from the Emporium contract itself to an attacker-chosen `endpoint` with attacker-chosen `callData`, gated only by two selector checks that do not cover `IERC20.transferFrom`: [3](#0-2) 

This is structurally identical to the `UnprotectedArbBot` bug class: a caller-supplied target + calldata forwarded via `.call()` by the contract itself, gated by an incomplete selector denylist instead of a real access-control/authorization check. In `UnprotectedArbBot` the exploited call was `WETH.transferFrom(owner, victim, amount)` using an allowance the owner had pre-granted to the victim contract; here the analogous call is `token.transferFrom(victimUser, attacker/emporium, amount)` using an allowance any user previously granted to the shared `Emporium` contract (which is the expected/legitimate flow for depositing into Emporium via a stateless "pull" op).

Because `runAction` is `onlyAllowedRecipient`-gated only at the Hinkal→Emporium boundary (i.e., it just requires the caller be Hinkal itself), any unprivileged EOA can drive this path by submitting their own valid `transact()` call (with a legitimate proof over their own, possibly zero-value, UTXOs) and supplying a malicious `externalActionMetadata` with `signerAddress = address(0)` and an op list containing:
```
{ endpoint: <victimToken>, invokeWallet: false, value: 0,
  callData: abi.encodeWithSelector(IERC20.transferFrom.selector, victimUser, address(this)/*Emporium*/, allowanceAmount) }
```
After this call, `runAction`'s balance-delta accounting at the end of the function sees a positive balance increase on Emporium and converts it into a real, spendable UTXO for the attacker via `handleOut`: [4](#0-3) 

The equality broken is the protocol's core UTXO-backing invariant: `utxoOut.amount` (a newly minted shielded credit for the attacker) is derived from tokens forcibly pulled from a third party's ERC20 allowance rather than tokens the attacker deposited or legitimately swapped for. The `_from` address in the forwarded `transferFrom` call is never checked against `msg.sender`/the prover's own address, and is never bound to any signer authorization because `signerAddress == address(0)` deliberately disables the EIP-712 signature check for this exact code path.

### Impact Explanation
This is a Critical finding: it is direct theft of a user's/relay's approved ERC20 balance and results in unbacked minting of shielded value for the attacker (a spendable UTXO created from funds the attacker never owned or deposited), which breaks Hinkal's balance/UTXO-backing invariant. Any address (user, relay, or another external action) that has ever approved the Emporium contract for an ERC20 token — a routine, expected state for interacting with the deposit-via-stateless-op flow — is at risk regardless of whether they ever call Emporium again.

### Likelihood Explanation
Likelihood is high for any protocol that has been used for any length of time: ERC20 approvals to a shared contract like Emporium routinely outlive the specific transaction they were granted for (partial consumption, `approve(max)` patterns, or a user simply not revoking). The attack requires no privileged role, no relayer, and no signature — only a normal, self-authorized `transact()` call with `signerAddress = address(0)`, which is an explicitly supported code path, not an edge case.

### Recommendation
Require a signature/EIP-712 check for every `EmporiumOperation` regardless of `stack.signerAddress`, or restrict the "Stateless Interaction" (CASE 2) `endpoint.call` to a strict allow-list of endpoints/selectors that cannot include arbitrary ERC20 `transferFrom`/`approve`-style calls with a `_from` other than `msg.sender` of the outer `transact()` call. At minimum, decode and validate that any `transferFrom`-shaped `callData` in a stateless op has `_from == circomData.externalActionData.externalAddress` (the actual depositor), not an arbitrary third party.

### Proof of Concept
1. VictimUser approves `Emporium` for `1000 USDC` as part of a legitimate stateless deposit flow, and only `100 USDC` is consumed that transaction, leaving `900 USDC` allowance outstanding (or VictimUser grants `approve(Emporium, type(uint256).max)`, a common wallet pattern).
2. Attacker, an unprivileged EOA with a valid Hinkal account/proof over their own (even zero-value) UTXOs, calls `Hinkal.transact()` with `circomData.externalActionData.externalAddress = Emporium` and `externalActionMetadata` encoding an `EmporiumStack` with `signerAddress = address(0)` and:
   `ops = [{ endpoint: USDC, invokeWallet: false, value: 0, callData: transferFrom(VictimUser, Emporium, 900e6) }]`.
3. `Hinkal._externalTransact` calls `EmporiumUpgradeable.runAction`; `verifyWallet` returns immediately (no signature required since `signerAddress == 0`); the op loop executes CASE 2, calling `USDC.transferFrom(VictimUser, Emporium, 900e6)` directly from Emporium — succeeds because VictimUser's allowance to Emporium covers it.
4. `runAction`'s balance-delta logic sees Emporium's USDC balance increase by 900e6 and calls `handleOut`, which transfers the 900 USDC out to `msg.sender` (attacker) and mints a `UTXO` of `900e6 USDC` credited to the attacker's shielded balance — funds stolen from VictimUser with no signature, no relay, and no privileged role involved.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-89)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );

        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L97-118)
```text
            // CASE 1: Stateful Interaction
            if (op.invokeWallet && stack.signerAddress != address(0)) {
                (success, err) = IHinkalWallet(stack.signerAddress)
                    .callHinkalWallet(op.endpoint, op.callData, op.value);
            }
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

            if (!success) {
                revert CallFailed(err);
            }
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-184)
```text
        payRelayFees(circomData, stack.signerAddress, deltaAmountChanges);

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

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
            }
        }

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
        }

        return utxoSet;
    }

    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
            circomData.stealthAddressStructure,
            circomData.timeStamp
        );
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
