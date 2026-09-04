### Title
Emporium `signerAddress == 0` + Min-proof path lets any depositor run unaccounted arbitrary calls as Emporium, draining its held balances - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, whose circuit (`MainEVMCircuitMin.circom`) proves nothing but `message == Poseidon(messageSeed)`. Combined with `EmporiumUpgradeable.runAction`'s `signerAddress == 0` branch, which skips all EIP-712 signature verification in `verifyWallet`, an attacker can submit an `EmporiumStack` whose `ops` make arbitrary low-level calls from Emporium's own address, while the post-op balance-accounting loop is a no-op because it only iterates `circomData.erc20TokenAddresses` (empty).

### Finding Description
The claimed equality is: *assets Emporium can move in a transaction == assets accounted for in `balancesBefore`/`balancesAfter`*. This breaks down as follows.

1. `CircomDataBuilder.formInputForCircom` (contracts/CircomDataBuilder.sol:134-148) selects `formInputEmporiumMin` whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`. [1](#0-0) 

2. `formInputEmporiumMin` only emits `emporiumMessage`, `timeStamp`, `calldataHash` as public signals — it never includes `getSignedMessageHash`, `rootHashHinkal`, nullifiers, or `amountChanges`. [2](#0-1) 

3. The corresponding circuit `MainEVMCircuitMin.circom` only constrains `message === Poseidon(messageSeed)` — a fact the attacker trivially self-generates with a freshly chosen private seed. No UTXO ownership, nullifier, or Merkle-inclusion fact is proven for this path. [3](#0-2) 

4. `dimensionsCheck` in `HinkalHelper.performHinkalChecks` forces every parallel array (`amountChanges`, `inputNullifiers`, `onChainCreation`, `slippageValues`, `outCommitments`) to length 0 when `tokenNumber == 0`, so the attacker spends zero nullifiers and proves zero UTXO ownership. [4](#0-3) 

5. `rootHashExists` only checks that the supplied root is present in the historical `roots` mapping with no expiry/decay — an attacker can pick any old, valid root simply to pass the check, since the Min path never binds this root to anything proven inside the circuit. [5](#0-4) 

6. In `EmporiumUpgradeable.runAction`, when `stack.signerAddress == address(0)`, `verifyWallet` returns immediately after marking `emporiumMessage` used — no ECDSA signature check occurs at all: [6](#0-5) 

7. The `ops` loop then executes attacker-controlled calls with Emporium as `msg.sender`, either through `IHinkalWallet.callHinkalWallet` (case 1, requires nonzero signer) or a raw low-level call to any endpoint with any calldata/value (case 2), which is fully reachable when `signerAddress == 0`: [7](#0-6) 

8. Post-op accounting only iterates `circomData.erc20TokenAddresses`, which the attacker fixed at length 0 to qualify for the Min path — so `balancesBefore`/`balancesAfter` are both empty arrays, and the loop that would normally revert on unexpected balance loss (`BalanceChangeShouldBePositive`) never runs for any token the arbitrary call actually touched: [8](#0-7) 

The attacker's exact call: submit `Hinkal.transact` with `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalAddress = <Emporium proxy>`, `erc20TokenAddresses = []`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack{signerAddress: address(0), ops: [EmporiumOperation{endpoint: <target token or router>, invokeWallet: false, value: 0, callData: <e.g. token.transfer(attacker, emporiumBalance)>}]})`, and a locally generated proof for `MainEVMCircuitMin` using any self-chosen `messageSeed`. `getHashedCalldata` still must match `calldataHash` (both are computed purely from calldata fields the attacker controls, so this is trivially satisfiable off-chain before submission) — it provides no protection against the missing signature/ownership binding.

None of the existing guards stop this: `performHinkalChecks` only checks `calldataHash` integrity and array-length dimensions, not ownership of any asset; `verifyProof` only proves knowledge of a self-chosen seed; `rootHashExists` accepts any historical root; `insertNullifiers` never runs because there are no nullifiers; and `onlyAllowedRecipient` is satisfied because the call legitimately originates from Hinkal.

### Impact Explanation
Any unprivileged address can force `EmporiumUpgradeable` to execute arbitrary external calls under its own identity with zero balance accounting, letting the attacker drain any ERC20 tokens or ETH sitting in the Emporium contract (e.g., left over from other users' in-flight Emporium operations or partially completed multi-step flows) to an address of their choosing, or invoke functions on any protocol that trusts `msg.sender == Emporium` (e.g., a router with a standing approval from Emporium). This is direct theft of protocol/in-flight user funds with no signature, nullifier, or ownership proof required — repeatable every block, matching the Critical severity category (direct theft of shielded or in-flight user funds; executing calls or moving assets never authorized by any prover).

### Likelihood Explanation
Preconditions are minimal and fully attacker-controlled: no privileged role, no valid UTXO, no signed EmporiumStack signature, and any historical Merkle root suffices. The only requirement is that Emporium holds some balance or approval at the time of attack, which is a normal and expected state given the code's own comment that Emporium is designed to sometimes carry a pre-existing balance across calls ("the only case when balanceChange can be < 0, when there were some funds on emporium before the call"). Attacker cost is a single proof generation for the trivial Min circuit and one `Hinkal.transact` call — fully feasible and repeatable.

### Recommendation
Do not allow the `signerAddress == 0` branch to execute arbitrary `ops` under the min-proof path. Either require `erc20TokenAddresses.length > 0` (and thus the full `formInputNormal`/`getSignedMessageHash` binding) whenever `ops` contains non-empty calldata, or require a valid signature (disallow `signerAddress == address(0)`) for any op that is not a pure no-value/no-calldata sentinel. Additionally, bind `stack.ops`/`signerAddress` into the Min circuit's public inputs (e.g., include `getSignedMessageHash` or an ops-hash) so the near-empty proof cannot authorize arbitrary external calls, and consider tracking/asserting Emporium's balance invariants independent of the caller-supplied `erc20TokenAddresses` array (e.g., disallow undeclared token/ETH balance changes during `runAction`).

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as an allowed recipient), and register `HINKAL_EMPORIUM_ACTION_ID -> Emporium` in `externalActionMap`.
2. Fund Emporium directly with 100 test ERC20 tokens (simulating leftover in-flight balance) — assert `token.balanceOf(emporium) == 100e18`.
3. Attacker (non-owner EOA) builds `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `inputNullifiers = []`, `outCommitments = []`, `onChainCreation = []`, `slippageValues = []`, `externalActionData = {externalAddress: emporium, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(token.transfer, (attacker, 100e18))}], maxFee:0, deadline: type(uint256).max})}`, a `rootHashHinkal`/`rootHashHinkalIndex` from any prior deposit (even old), `calldataHash = getHashedCalldata(circomData)`.
4. Generate a locally-computed `MainEVMCircuitMin` proof for a freshly chosen `messageSeed` with `message = Poseidon(messageSeed)` set as `emporiumMessage`.
5. Call `Hinkal.transact(a, b, c, dimensions{tokenNumber:0, nullifierAmount:0, outputAmount:0}, circomData)` from the attacker EOA.
6. Assert: `token.balanceOf(emporium) == 0` and `token.balanceOf(attacker) == 100e18` after the call, proving the equality "assets moved == assets accounted for in balancesBefore/After" is violated (accounted delta was 0 for the empty token array, but real delta was 100e18).

### Citations

**File:** contracts/CircomDataBuilder.sol (L134-148)
```text
    function formInputForCircom(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory) {
        if (
            circomData.externalActionData.externalActionId ==
            HINKAL_EMPORIUM_ACTION_ID &&
            circomData.erc20TokenAddresses.length == 0
        ) {
            return formInputEmporiumMin(circomData);
        } else {
            return formInputNormal(chainId, verifyingContract, circomData);
        }
    }
```

**File:** contracts/CircomDataBuilder.sol (L150-161)
```text
    function formInputEmporiumMin(
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);

        uint16 index = 0;

        input[index++] = circomData.emporiumMessage;

        input[index++] = circomData.timeStamp;
        input[index++] = circomData.calldataHash;
    }
```

**File:** circuits/MainEVMCircuitMin.circom (L1-18)
```text

pragma circom 2.1.6;

include "../../node_modules/circomlib/circuits/poseidon.circom";

template MainEVMCircuitMin() {
  // Public inputs:
  signal input outTimeStamp;
  signal input calldataHash;

  // Private inputs:
  signal input messageSeed;

  // outputs:
  signal output message;

  message <== Poseidon(1)([messageSeed]);
}
```

**File:** contracts/HinkalHelper.sol (L64-105)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
        require(
            circomData.amountChanges.length == dimensions.tokenNumber,
            "AmountChanges number should be equal to token number"
        );

        require(
            circomData.onChainCreation.length == dimensions.tokenNumber,
            "onchain creation is equal to tokens count"
        );

        require(
            circomData.slippageValues.length == dimensions.tokenNumber,
            "slippageValues length should be equal to tokens count"
        );

        require(
            circomData.inputNullifiers.length == dimensions.tokenNumber,
            "InputNullifiers number should be equal to token number"
        );

        uint previousNullifierAmount = circomData.inputNullifiers.length > 0
            ? circomData.inputNullifiers[0].length
            : 0;
        for (uint i = 1; i < circomData.inputNullifiers.length; i++) {
            require(
                circomData.inputNullifiers[i].length == previousNullifierAmount,
                "Nullifier amount should be equal"
            );
        }
        require(
            previousNullifierAmount == dimensions.nullifierAmount,
            "Actual and Claimed Nullifier Amount should be equal"
        );

```

**File:** contracts/MerkleBase.sol (L53-64)
```text
    function rootHashExists(
        uint256 _root,
        uint256 _rootIndex
    ) public view returns (bool) {
        if (m_index == MINIMUM_INDEX) {
            return _root == 0;
        }
        if (_rootIndex < MINIMUM_INDEX || _rootIndex >= m_index) {
            return false;
        }
        return _root != 0 && roots[_rootIndex] == _root;
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-118)
```text
        for (uint256 i = 0; i < stack.ops.length; i++) {
            EmporiumOperation memory op = stack.ops[i];

            bool success;
            bytes memory err;

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-160)
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
