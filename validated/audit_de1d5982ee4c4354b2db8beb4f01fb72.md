## No vulnerability found for this question.

**Reasoning:** The claimed equality break does not exist. `_createProoflessDepositCommitments` calls `createOnchainCommitment`, which computes the leaf commitment as `hash4(utxo.amount, utxo.erc20Address, utxo.stealthAddressStructure.stealthAddress, utxo.timeStamp)` directly inside the Hinkal contract itself using the `amounts[i]`/`erc20Addresses[i]` values passed to `prooflessDeposit` — these are not attacker-controlled independent of the actual deposit. [1](#0-0) 

Before the commitment is created, `_handleTransfersFromProoflessDeposit` enforces that the actual on-chain balance change for each token equals the sum of `amounts[i]` for that token (`balanceAfter - balanceBefore == amount`), so the `amount`/`erc20Address` baked into the leaf are provably backed by real transferred funds. [2](#0-1) 

The only attacker-controlled, unvalidated fields are `H0x, H0y, H1x, H1y, stealthAddress`, which affect only *who can later derive spending authority* over the UTXO (the stealth-address key-derivation scheme), not the `amount`/`erc20Address` encoded in the commitment. When the UTXO is later spent via `transact`, the circuit recomputes the commitment via `OriginalCommitmentCalculator` using the spender-supplied `amount`/`erc20TokenAddress` and the derived `publicKey` (from `StealthAddressCalculator` using `H0Ax/H0Ay`), and this recomputed commitment must match a Merkle leaf whose root equals `rootHashHinkal`. [3](#0-2) [4](#0-3) 

Because the leaf hash directly encodes the true `amount` and `erc20Address` at mint time (enforced by the balance check), any spend attempt with a different `amount`/`erc20Address` produces a different `calcCommitment[i][j].out`, causing the Merkle root check (`calcEqual[i][j]`) to fail — the spend simply reverts rather than allowing divergence. The unvalidated `stealthAddressStructure` fields only risk the depositor being unable to derive spending rights over their own self-created UTXO (a self-custody concern, not a proof bypass), which does not constitute theft of another party's funds or a nullifier/proof bypass under the stated impact categories.

### Citations

**File:** contracts/HinkalBase.sol (L53-62)
```text
    function createOnchainCommitment(
        UTXO memory utxo,
        bytes calldata onChainEncryptedOutput
    ) internal view returns (OnChainCommitment memory) {
        uint256 commitment = hash4(
            utxo.amount,
            uint256(uint160(utxo.erc20Address)),
            utxo.stealthAddressStructure.stealthAddress,
            utxo.timeStamp
        );
```

**File:** contracts/Hinkal.sol (L356-380)
```text
    function _handleTransfersFromProoflessDeposit(
        TokenWithAmount[] memory uniqueTokens,
        uint256 uniqueCount
    ) private {
        for (uint256 i = 0; i < uniqueCount; i++) {
            address erc20Address = uniqueTokens[i].erc20Address;
            uint256 amount = uniqueTokens[i].amount;

            uint256 balanceBefore = getERC20OrETHBalance(erc20Address);
            if (erc20Address == address(0)) balanceBefore -= msg.value;

            transferERC20TokenFromOrCheckETH(
                erc20Address,
                msg.sender,
                address(this),
                amount
            );

            uint256 balanceAfter = getERC20OrETHBalance(erc20Address);

            require(
                balanceAfter - balanceBefore == amount,
                "proofless deposit balances must be equal"
            );
        }
```

**File:** circuits/OriginalCommitmentCalculator.circom (L6-23)
```text
template OriginalCommitmentCalculator() {
  signal input amount;
  signal input erc20TokenAddress;
  signal input publicKey;
  signal input timeStamp;
  signal output out;

  component calcIsAmountZero = IsZero();
  calcIsAmountZero.in <== amount;

  component calcCommitment = Poseidon(4);
  calcCommitment.inputs[0] <== amount;
  calcCommitment.inputs[1] <== erc20TokenAddress;
  calcCommitment.inputs[2] <== publicKey;
  calcCommitment.inputs[3] <== timeStamp;

  out <== calcCommitment.out * (1 - calcIsAmountZero.out);
}
```

**File:** circuits/MainEVMCircuit.circom (L114-148)
```text
        // 1) Calculating Commitments for Input UTXOs
        calcCommitment[i][j] = OriginalCommitmentCalculator();
        calcCommitment[i][j].amount <== inAmounts[i][j];
        calcCommitment[i][j].erc20TokenAddress <== erc20TokenAddresses[i];
        calcCommitment[i][j].publicKey <== calcInPublicKeys[i][j].out;
        calcCommitment[i][j].timeStamp <== inTimeStamps[i][j];

        preventInOverflow[i][j] = OverflowPreventer(inputCount);
        preventInOverflow[i][j].in <== inAmounts[i][j];

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
