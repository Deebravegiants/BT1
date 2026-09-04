## Finding: Valid

### Title
Unauthenticated theft of Emporium-held funds via zero-length token array + `signerAddress == 0` Min-circuit bypass - (File: `contracts/CircomDataBuilder.sol`, `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, which only proves `message == Poseidon(messageSeed)` — a fact any party can trivially satisfy without owning any UTXO, nullifier, or Merkle root membership [1](#0-0) . Combined with `EmporiumUpgradeable.verifyWallet` skipping all signature checks when `stack.signerAddress == address(0)` [2](#0-1) , and `runAction`'s balance accounting operating solely on the (empty) `erc20TokenAddresses` array while the actual `stack.ops` executed are unconstrained by that array [3](#0-2) , an attacker can drive Emporium to execute arbitrary calls (e.g. `approve()`/`transfer()`) on any token it holds, from the Emporium contract's own identity, with zero on-chain accounting of the resulting asset movement.

### Finding Description
The claimed equality is: **assets Emporium can move in a transaction == assets accounted for in `balancesBefore`/`balancesAfter`.** This is broken as follows.

1. `formInputForCircom` selects the Min-input path purely based on `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` [4](#0-3) . `formInputEmporiumMin` builds public inputs from only `emporiumMessage`, `timeStamp`, `calldataHash` [5](#0-4) .
2. `MainEVMCircuitMin` only constrains `message <== Poseidon(1)([messageSeed])` [6](#0-5) , with no root-hash, nullifier, spending-key, or signature checks (unlike `MainEVMCircuit`, which enforces `inNullifiers === calcNullifier.out` and root-hash equality per UTXO) [7](#0-6) . `messageSeed` is a private value the attacker freely chooses, so any unprivileged party can generate a valid Min proof for `emporiumMessage = Poseidon(any seed)` — this proves nothing about ownership of shielded funds or authorization.
3. `Hinkal.transact` validates the proof and the calldata self-hash, then calls into `_externalTransact` → `EmporiumUpgradeable.runAction` [8](#0-7) . `dimensionsCheck` only requires internal consistency between `dimensions.tokenNumber` and the (empty) arrays — nothing prevents `tokenNumber == 0` [9](#0-8) .
4. Inside `runAction`, `EmporiumStack` (including `stack.ops` and `stack.signerAddress`) is decoded entirely from attacker-supplied `externalActionData.externalActionMetadata` [10](#0-9) . When `stack.signerAddress == address(0)`, `verifyWallet` merely marks `emporiumMessage` used and returns — no EIP-712 signature check is performed at all [11](#0-10) .
5. The ops loop then executes `op.endpoint.call{value: op.value}(op.callData)` with `msg.sender == Emporium` for every op in `stack.ops`, completely independent of `circomData.erc20TokenAddresses` (which is empty) [12](#0-11) . An op such as `ERC20(token).approve(attacker, type(uint256).max)` or `ERC20(token).transfer(attacker, balance)` executes with Emporium's identity.
6. `balancesBefore`/`balancesAfter` are computed via `getBalancesForArray(circomData.erc20TokenAddresses)`, which is an empty array, so both are zero-length; the subsequent balance-change/UTXO-creation loop also iterates zero times [13](#0-12) . The outer `Hinkal.transact` loop that enforces `slippageValues`/`balanceDif` also iterates over the same empty `erc20TokenAddresses` array [14](#0-13) .

Net effect: any token/asset the Emporium contract is currently holding (residual balances from other in-flight multi-op user transactions, dust, or standing approvals left after prior legitimate operations — explicitly acknowledged by the comment "the only case when balanceChange can be < 0, when there were some funds on emporium before the call") can be drained or granted away to the attacker with **no accounting check, no signature check, and no real zero-knowledge proof of authorization**.

### Impact Explanation
Direct theft of assets custodied by the Emporium contract — funds that other users have in flight through multi-step Emporium operations (swaps, approvals routed through Emporium) or standing balances left on the contract. This is unauthenticated (no signature, no valid UTXO ownership needed) and repeatable for as long as Emporium holds any token balance, matching the **Critical** severity category (direct theft of shielded or in-flight user funds).

### Likelihood Explanation
Preconditions are minimal and entirely attacker-controlled: no deposit, no existing UTXO, no relay privilege is required — only a self-generated Groth16 proof for `MainEVMCircuitMin` (a trivial circuit with one Poseidon constraint) and a crafted `EmporiumStack` with `signerAddress == address(0)`. Cost is a single transaction's gas plus proof generation. This is repeatable every time Emporium holds any balance, and is trivially combined with the attacker's own sandwiching deposit/op sequence to guarantee Emporium is holding attacker-tunable balances at exploit time.

### Recommendation
- Do not allow `signerAddress == address(0)` to bypass authorization entirely; the Min-circuit path should either forbid unsigned `EmporiumStack`s or require the Min proof itself to bind (via public input) a commitment over `stack.ops`/`stack.signerAddress` so a valid proof cannot be forged without real authorization.
- Make `EmporiumUpgradeable.runAction`'s balance accounting independent of `circomData.erc20TokenAddresses` — derive the token set to check from the actual `endpoint`/`callData` touched by `stack.ops`, or require `erc20TokenAddresses` to be non-empty and inclusive of every token any op could affect, enforced on-chain.
- Reject `erc20TokenAddresses.length == 0` combined with `externalActionId == HINKAL_EMPORIUM_ACTION_ID` unless the ops are provably read-only / non-value-moving, or add explicit whitelisting of allowed selectors/endpoints for the min-proof path.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register the Min-circuit verifier for `buildVerifierId({tokenNumber:0, nullifierAmount:0, outputAmount:0}, HINKAL_EMPORIUM_ACTION_ID)`.
2. Fund Emporium directly with `TOKEN.transfer(emporium, 1000e18)` to simulate residual/in-flight balance.
3. As an unprivileged attacker EOA, generate a `MainEVMCircuitMin` proof for `messageSeed = 1`, set `emporiumMessage = Poseidon(1)`.
4. Build `circomData` with `erc20TokenAddresses = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: address(TOKEN), invokeWallet: false, value: 0, callData: abi.encodeCall(TOKEN.transfer, (attacker, 1000e18))})], maxFee:0, deadline:0}))`, matching `calldataHash`.
5. Call `Hinkal.transact(a, b, c, dimensions{0,0,0}, circomData)` from attacker.
6. Assert `TOKEN.balanceOf(attacker)` increased by `1000e18` and `TOKEN.balanceOf(emporium)` decreased by `1000e18`, with no revert from slippage/balance checks, proving the equality (`assets moved == assets accounted`) is broken. [1](#0-0) [15](#0-14) [6](#0-5)

### Citations

**File:** contracts/CircomDataBuilder.sol (L134-161)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-159)
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

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
        }

        return utxoSet;
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

**File:** circuits/MainEVMCircuit.circom (L124-148)
```text
        // 2) Calculating Nullifier from commitment and signature
        calcSignature[i][j] = Signature();
        calcSignature[i][j].nullifyingPrivateKey <== nullifyingPrivateKey;
        calcSignature[i][j].commitment <== calcCommitment[i][j].out;

        calcNullifier[i][j] = NullifierCalculator();
        calcNullifier[i][j].commitment <== calcCommitment[i][j].out;
        calcNullifier[i][j].signature <== calcSignature[i][j].out;

        // 3) Checking that nullifier is legit
        inNullifiers[i][j] === calcNullifier[i][j].out;

        // 4) Calculating Transaction Root Hash
        calcTransactionRootHash[i][j] = MerkleRootCalculator(treeDepth);
        calcTransactionRootHash[i][j].inCommitment <== calcCommitment[i][j].out;
        for (var k = 0; k < treeDepth; k++) {
          calcTransactionRootHash[i][j].commitmentSiblings[k] <== inCommitmentSiblings[i][j][k];
          calcTransactionRootHash[i][j].commitmentSiblingSides[k] <== inCommitmentSiblingSides[i][j][k];
        }

        // 5) Checking that transaction root hash is legit
        calcEqual[i][j] = ForceEqualIfEnabled();
        calcEqual[i][j].in[0] <== calcTransactionRootHash[i][j].rootHash;
        calcEqual[i][j].in[1] <== rootHashHinkal;
        calcEqual[i][j].enabled <== inAmounts[i][j];
```

**File:** contracts/Hinkal.sol (L30-66)
```text
    function transact(
        uint256[2] calldata a,
        uint256[2][2] calldata b,
        uint256[2] calldata c,
        Dimensions calldata dimensions,
        CircomData calldata circomData
    ) public payable nonReentrant {
        {
            uint256[] memory inputForCircom = hinkalHelper.performHinkalChecks(
                circomData,
                dimensions,
                msg.sender
            );

            require(
                verifyProof(
                    a,
                    b,
                    c,
                    inputForCircom,
                    buildVerifierId(
                        dimensions,
                        circomData.externalActionData.externalActionId
                    )
                ),
                "Invalid Proof"
            );
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
            );
        }
        hinkalHelper.performSideEffects(circomData);
```

**File:** contracts/Hinkal.sol (L76-121)
```text
            UTXO[] memory utxoSet;

            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }

            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            OnChainCommitment[]
                memory onChainCommitments = new OnChainCommitment[](
                    utxoSet.length
                );
            uint256 onChainCommitmentCounter = 0;
            for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
                int256 balanceDif;

                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
                );

                uint256 utxoAmount = 0;
                for (uint j = 0; j < utxoSet.length; j++) {
                    if (
                        utxoSet[j].erc20Address ==
                        circomData.erc20TokenAddresses[i]
                    ) {
```

**File:** contracts/HinkalHelper.sol (L64-90)
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
```
