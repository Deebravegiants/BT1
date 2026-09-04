### Title
Attacker-controlled `originalSender` + caller-chosen recipient in `DepositOnChainUtxosExternalAction` allows unauthorised `transferFrom` - (File: `contracts/external-actions/DepositOnChainUtxosExternalAction.sol`)

### Summary
`DepositOnChainUtxosExternalAction.runAction` pulls ERC20 tokens from `circomData.originalSender` via `transferERC20TokenFrom` and credits the resulting shielded UTXO to `circomData.stealthAddressStructure` and `circomData.timeStamp` — both of which are plain calldata fields chosen by whoever builds the `CircomData` struct for the `transact()` call, not values that are bound to `msg.sender`/the signer for this specific action. This mirrors the report's bug class of "a value used in a critical calculation that is supposed to reflect ground truth (in the original finding, real elapsed time driving APR) but is instead taken from an attacker/caller supplied field" — here, the UTXO's `timeStamp` (and implicitly which address is *charged*) is fully caller-determined rather than derived from `block.timestamp`, as the file's own docstring states.

### Finding Description
`createOnchainCommitment` in `contracts/HinkalBase.sol:53-70` computes the on-chain leaf as `hash4(amount, erc20Address, stealthAddress, utxo.timeStamp)`. For the ordinary proofless-deposit path (`Hinkal.sol:331-354`), `timeStamp` is hard-set to `block.timestamp`. For `DepositOnChainUtxosExternalAction.sol:66-72`, however, the UTXO's `timeStamp` is `circomData.timeStamp + utxoIndex` — a value taken straight from the caller-supplied `CircomData`, as explicitly documented in the contract's own comment: *"creates on-chain UTXOs whose commitments are fully determined by the caller, because their timestamps come from `circomData.timeStamp` rather than from the block."* [1](#0-0) [2](#0-1) [3](#0-2) 

At the same time, this on-chain leaf is never checked by the ZK circuit: `checkOnchainCreation` in `HinkalHelper.sol` only enforces `amountChanges[i] == 0` and zeroed `inputNullifiers` for `onChainCreation` entries — it does not constrain `stealthAddressStructure` or `timeStamp` against any circuit-verified public input. [4](#0-3) 

Separately, the token pull itself is authorised only by ERC20 `allowance`, not by any signature/nullifier check: `transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal)` is called with `userAddress = circomData.originalSender`, a plain address field. [5](#0-4) [6](#0-5) 

I was unable to locate, within the files I could inspect, an explicit on-chain check binding `circomData.originalSender` to `msg.sender` or to a signature specifically for this action's deposit path (the `performHinkalChecks`/`HinkalHelper.sol` logic I could read did not show such a binding for this code path). If no such binding exists, any EOA can call `transact()` targeting this external action with `circomData.originalSender` set to a victim address that has an outstanding ERC20 allowance to the Hinkal/external-action contract (e.g., left over from a prior legitimate deposit), and `circomData.stealthAddressStructure` set to the attacker's own key material, pulling the victim's tokens into a shielded UTXO the attacker controls.

### Impact Explanation
If `originalSender` is not cryptographically bound to the actual token owner/signer, this breaks the "`transferFrom` authorised by the prover or signer" invariant: an unprivileged EOA could move a third party's approved ERC20 balance into a shielded UTXO under the attacker's own stealth address — direct theft of user funds, matching the Critical/High impact bar in the rules.

### Likelihood Explanation
Exploitability depends entirely on whether `circomData.originalSender` is validated elsewhere (a check I could not confirm or rule out with the code available to me). If unvalidated, likelihood is high since it requires only a standard, unprivileged `transact()` call with attacker-crafted `CircomData` and a victim who has any lingering allowance to the contract. This is a real caveat: I could not fully trace `HinkalHelper.performHinkalChecks` (only partial excerpts were available) to confirm or deny an `originalSender`/signer binding.

### Recommendation
Bind `circomData.originalSender` (or the equivalent field used by each external action) to `msg.sender` of the `transact()` call, or require a signature over it that is included in the circuit's public inputs, so that no caller can name an arbitrary third party as the token source. Additionally, either derive on-chain UTXO `timeStamp` values from `block.timestamp` (as done in the standard proofless-deposit path) or include `circomData.timeStamp`/`stealthAddressStructure` for `onChainCreation` entries in the circuit's verified public inputs so the leaf actually reflects an authenticated value.

### Proof of Concept
Conceptual (not fully verified against the complete `HinkalHelper.performHinkalChecks` logic, which I could not read in full):
1. Victim `V` previously approved token allowance to the Hinkal/ExternalAction contract as part of a legitimate deposit flow, leaving unused allowance.
2. Attacker `A` calls `Hinkal.transact()` with `circomData.originalSender = V`, `circomData.externalActionData.externalActionId` pointing at `DepositOnChainUtxosExternalAction`, `circomData.stealthAddressStructure` set to `A`'s own key, and `amountChanges[i] = 0` (required by `checkOnchainCreation`).
3. `DepositOnChainUtxosExternalAction.runAction` calls `transferERC20TokenFrom(token, V, contract, amount)`, pulling `V`'s tokens, and creates an on-chain UTXO commitment keyed to `A`'s stealth address via `createOnchainCommitment` (`HinkalBase.sol:53-70`), using attacker-chosen `circomData.timeStamp`.
4. `A` later spends this UTXO using their own private key — funds that originated from `V`'s allowance are now solely under `A`'s control. [7](#0-6)

### Citations

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L10-13)
```text
/// @title DepositOnChainUtxosExternalAction
/// @notice Deposits tokens into Hinkal and creates on-chain UTXOs whose commitments
/// are fully determined by the caller, because their timestamps come from
/// circomData.timeStamp rather than from the block.
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L21-86)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmounts
    ) external override onlyAllowedRecipient returns (UTXO[] memory utxoSet) {
        uint256 tokenCount = circomData.erc20TokenAddresses.length;
        require(
            tokenCount > 0 && deltaAmounts.length == tokenCount,
            "DepositOnChainUtxosExternalAction: token count mismatch"
        );

        address userAddress = circomData.originalSender;
        require(
            userAddress != address(0),
            "DepositOnChainUtxosExternalAction: Invalid originalSender"
        );

        uint256[][] memory utxoAmounts = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (uint256[][])
        );
        require(
            utxoAmounts.length == tokenCount,
            "DepositOnChainUtxosExternalAction: metadata length mismatch"
        );

        utxoSet = new UTXO[](countUtxos(utxoAmounts));

        uint256 utxoIndex = 0;
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );

            address tokenAddress = circomData.erc20TokenAddresses[i];
            uint256 tokenTotal = 0;

            for (uint256 j = 0; j < utxoAmounts[i].length; j++) {
                uint256 amount = utxoAmounts[i][j];
                require(
                    amount > 0,
                    "DepositOnChainUtxosExternalAction: UTXO amount must be positive"
                );
                tokenTotal += amount;

                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
            }

            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
        }

        emit BlockedUtxosCreated();
    }
```

**File:** contracts/HinkalBase.sol (L53-70)
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

        OnChainCommitment memory onChainCommitment = OnChainCommitment({
            utxo: utxo,
            commitment: commitment,
            onChainEncryptedOutput: onChainEncryptedOutput
        });
        return onChainCommitment;
    }
```

**File:** contracts/HinkalHelper.sol (L173-202)
```text
    function checkOnchainCreation(
        CircomData calldata circomData
    ) internal pure {
        bool isInternalTransaction = circomData
            .externalActionData
            .externalActionId == 0;

        for (uint i = 0; i < circomData.onChainCreation.length; i++) {
            if (circomData.onChainCreation[i]) {
                require(
                    !isInternalTransaction,
                    "onChainCreation not allowed for internal transactions"
                );
                require(
                    circomData.amountChanges[i] == 0,
                    "amountChanges must be zero when onChainCreation is true"
                );
                for (
                    uint j = 0;
                    j < circomData.inputNullifiers[i].length;
                    j++
                ) {
                    require(
                        circomData.inputNullifiers[i][j] == 0,
                        "inputNullifiers must be zero when onChainCreation is true"
                    );
                }
            }
        }
    }
```
