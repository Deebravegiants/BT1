### Title
Emporium `runAction` skips all authorization when `signerAddress == address(0)`, letting an unprivileged prover drain Emporium's balance via the min-circuit path — (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
When `Hinkal.transact` is called with `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, whose corresponding circuit (`MainEVMCircuitMin.circom`) only proves `message == Poseidon(messageSeed)` and leaves `calldataHash`/`outTimeStamp` completely unconstrained. Combined with `EmporiumUpgradeable.verifyWallet` returning immediately (no EIP‑712 signature check) whenever `stack.signerAddress == address(0)`, an attacker can drive `runAction` to execute arbitrary `op.endpoint.call{value: op.value}(op.callData)` calls from Emporium's identity with zero balance accounting, since the balances loop iterates the (deliberately empty) `erc20TokenAddresses` array.

### Finding Description
The broken equality is: *assets Emporium can move in a transaction == assets accounted for in `balancesBefore`/`balancesAfter`*.

- `CircomDataBuilder.formInputForCircom` selects the min path solely based on `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`: [1](#0-0) 

- `formInputEmporiumMin` only feeds `emporiumMessage`, `timeStamp`, `calldataHash` into the proof's public-input vector: [2](#0-1) 

- The matching circuit `MainEVMCircuitMin` constrains nothing except `message <== Poseidon(1)([messageSeed])`; `calldataHash` and `outTimeStamp` are unconstrained public signals the prover can freely choose: [3](#0-2) 

- `performHinkalChecks` only verifies that the supplied `calldataHash` matches a rehash of the calldata (a self-consistency check, not an ownership/authorization check), then calls `formInputForCircom`: [4](#0-3) 

- In `EmporiumUpgradeable.runAction`, the attacker-controlled `EmporiumStack` is ABI-decoded straight from `externalActionData.externalActionMetadata`, and `verifyWallet` is called before executing ops: [5](#0-4) 

- Critically, `verifyWallet` performs **zero** signature/authorization checks when `signerAddress == address(0)` — it just marks `usedMessages[emporiumMessage] = true` and returns: [6](#0-5) 

- The only restriction on the stateless op path is a selector blacklist for `callHinkalWallet`/`doSendToRelay`; any other `endpoint`/`callData`/`value` is executed via low-level `call`: [7](#0-6) 

- Because the attacker chose `erc20TokenAddresses.length == 0` to reach the min path, `balancesBefore`/`balancesAfter`/the accounting loop are all empty and enforce nothing: [8](#0-7) 

**Exploit flow:** An unprivileged attacker (1) picks any unused `messageSeed`, computes `emporiumMessage = Poseidon(messageSeed)`; (2) builds `CircomData` with `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalAddress = <Emporium>`, `erc20TokenAddresses = []`; (3) sets `externalActionMetadata = abi.encode(EmporiumStack{v:0,r:0,s:0,signerAddress:address(0), ops:[{endpoint: <target>, invokeWallet:false, value:<amount>, callData:<arbitrary>}], maxFee:0, deadline:<future>})`; (4) computes `calldataHash` locally and generates a valid Groth16 proof for `MainEVMCircuitMin` (trivial, since only `messageSeed` knowledge is required — no secret UTXO data); (5) calls `Hinkal.transact`. `performHinkalChecks` and `verifyProof` pass (the proof legitimately satisfies the trivial circuit), `rootHashExists` passes with any historical root, and `EmporiumUpgradeable.runAction` executes the attacker's arbitrary call using Emporium's own held funds, with no balance-based revert since the token array is empty.

Existing guards (`performHinkalChecks`, `verifyProof`, `rootHashExists`, `onlyAllowedRecipient`) do not prevent this because none of them binds the min-path proof to any real ownership fact — the min circuit is intentionally minimal and defers all authorization to `verifyWallet`'s EIP-712 check, which is bypassed entirely by the `signerAddress == address(0)` branch.

### Impact Explanation
Any ETH/token balance sitting in the `EmporiumUpgradeable` contract (leftover relay fees, in-flight funds from multi-step operations, or funds accidentally/temporarily routed through Emporium) can be moved to an attacker-controlled endpoint or used to fund an arbitrary external call performed with Emporium's identity (`msg.sender == Emporium`), with no proof-verified ownership and no balance accounting. This is a direct theft primitive for shielded/in-flight/protocol funds held by Emporium, and is repeatable per unused `emporiumMessage` — Critical severity (direct theft of shielded or in-flight user funds; executing calls a wallet owner never authorised).

### Likelihood Explanation
Preconditions are minimal and fully attacker-controlled: no special role, no victim cooperation, and no non-trivial cryptographic secret (the min-circuit's only "private" input is a self-chosen `messageSeed`). The only requirement is that Emporium holds some balance to steal or that some external endpoint honors Emporium as a trusted caller. Attacker cost is a single proof generation (public circuit, publicly available proving artifacts) and one transaction — highly feasible and repeatable.

### Recommendation
Do not allow `verifyWallet` to silently skip authorization when `signerAddress == address(0)`. Either remove the unauthenticated/self-executing branch entirely, or require that `signerAddress == address(0)` only be usable when the min-circuit itself constrains a meaningful authorization fact (e.g., binding `calldataHash`/ops hash into a genuinely proof-verified signal, not merely a free public input). Additionally, enforce that the min-path can only be used for genuinely balance-free operations by having `EmporiumUpgradeable.runAction` reject non-empty `stack.ops[].value` and non-zero-value external calls when `erc20TokenAddresses.length == 0`, or require `erc20TokenAddresses`/accounting to always reflect any assets an op can move regardless of path.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (registered under `HINKAL_EMPORIUM_ACTION_ID`), and a `MockVerifier`/real min-circuit verifier plus a locally-generated Groth16 proof for `MainEVMCircuitMin` using an attacker-chosen `messageSeed`.
2. Fund `EmporiumUpgradeable` with e.g. 10 ETH (simulate leftover/in-flight funds) — assert `address(emporium).balance == 10 ether`.
3. Craft `CircomData` with `erc20TokenAddresses = []`, `externalActionData = {externalAddress: emporium, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: attacker, invokeWallet: false, value: 10 ether, callData: ""}], maxFee:0, deadline: block.timestamp+1000, v:0, r:0, s:0})}`, correct `calldataHash`, valid `rootHashHinkal`/index from an existing deposit.
4. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from an unprivileged attacker EOA.
5. Assert equality broken: `address(emporium).balance` before (10 ether) != after (0), and `attacker.balance` increased by 10 ether — with no revert from `BalanceChangeShouldBePositive` (loop never runs) and no relay-fee enforcement, proving assets moved were never accounted for anywhere in `balancesBefore`/`balancesAfter`.

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

**File:** contracts/HinkalHelper.sol (L208-236)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
        relayerIsValid(circomData.relay);
        dimensionsCheck(circomData, dimensions);
        checkOnchainCreation(circomData);

        return
            CircomDataBuilder.formInputForCircom(
                block.chainid,
                hinkalAddress,
                circomData
            );
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-151)
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
