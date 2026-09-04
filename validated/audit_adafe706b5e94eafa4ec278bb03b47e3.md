### Title
Unauthenticated `circomData.originalSender` allows arbitrary `transferFrom` of a third party's approved ERC20 tokens - (File: `contracts/external-actions/DepositOnChainUtxosExternalAction.sol`)

### Summary
`DepositOnChainUtxosExternalAction.runAction` pulls ERC20 tokens via `transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal)` where `userAddress = circomData.originalSender` [1](#0-0) [2](#0-1) . The only check performed on this address is `userAddress != address(0)`, and this field is not bound into the value the ZK proof authenticates.

### Finding Description
The `getSignedMessageHash` function in `CircomDataBuilder.sol` — which is hashed into the circuit's `signedMessageHash` public signal and thus the value the Groth16 proof (and the caller's EdDSA spending signature) actually commits to — only encodes `chainId`, `verifyingContract`, `rootHashHinkal`, the ERC20 token list, `amountChanges`, `timeStamp`, `inputNullifiers`, `outCommitments`, `calldataHash`, `emporiumMessage`, and the stealth-address structure [3](#0-2) . `circomData.originalSender` is absent from this hash and from the public-signal array built in `formBasicInput`/`formInputNormal` [4](#0-3) .

Because `originalSender` is not constrained by the proof, calldata hash, or any signature, any caller of `Hinkal.transact` can set `circomData.originalSender` to an arbitrary address in the transaction's calldata. When the external action ID routes to `DepositOnChainUtxosExternalAction`, this address is used directly as the `from` argument of `safeTransferFrom`:

```solidity
address userAddress = circomData.originalSender;
require(userAddress != address(0), "...Invalid originalSender");
...
transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal);
``` [5](#0-4) 

`transferERC20TokenFrom` is a plain `safeTransferFrom` that succeeds as long as `userAddress` has previously granted an ERC20 allowance to this external action contract (`msg.sender` inside `runAction`) [6](#0-5) . Since legitimate users of the "blocked UTXO" / on-chain deposit flow must approve this exact contract to deposit tokens, any user who has an outstanding (non-zero, non-fully-consumed) allowance to `DepositOnChainUtxosExternalAction` is a valid victim: an unrelated attacker can craft a `circomData` blob naming that victim as `originalSender`, mint UTXOs for themselves inside the shielded pool for the pulled amount, while the tokens are actually debited from the victim's wallet.

This is directly analogous to the referenced report's root cause: an address/parameter accepted by a privileged "pull funds and mint value" function is not tied to any authenticated commitment (there, the Yield/Sense pool address; here, `originalSender`), letting an attacker mint pool value backed by someone else's funds instead of their own.

### Impact Explanation
This breaks the balance/backing equality of the shielded pool: shielded UTXOs are minted for the attacker while the underlying ERC20 balance is debited from a victim who never signed or proved anything related to this deposit. This is unauthorized `transferFrom` execution — asset movement the token owner never authorized through the prover/signer — and results in direct theft of the victim's approved ERC20 balance credited as shielded value to the attacker. This matches the Critical bar ("direct theft of ... user funds, minting shielded value without backing").

### Likelihood Explanation
Exploitability depends on finding an address with a residual, non-revoked allowance to the `DepositOnChainUtxosExternalAction` contract. Because the deposit flow is designed around exact per-deposit amounts and does not appear to force allowance-to-zero after use (unlike `approveERC20Token` used internally for router approvals), users who approve a round or larger amount than immediately consumed, or who approve once and deposit multiple times, remain exposed indefinitely. The attack requires no privileged role — only the ability to submit a `transact` call with attacker-chosen `circomData`, which is the standard unprivileged entry point.

### Recommendation
Bind `originalSender` into the ZK-proof-authenticated data (include it in `getSignedMessageHash`/the public-input vector in `CircomDataBuilder.sol`), and additionally require `circomData.originalSender == msg.sender` (the actual `transact` caller) inside `DepositOnChainUtxosExternalAction.runAction`, so the address whose tokens are pulled is cryptographically tied to the transaction sender/prover and cannot be substituted by a third party.

### Proof of Concept
1. Victim `V` calls `approve(DepositOnChainUtxosExternalAction, 1000)` for token `T` intending to deposit 1000 tokens as blocked UTXOs, but only deposits 400, leaving an allowance of 600.
2. Attacker `A` (no relation to `V`) crafts a valid ZK proof for `Hinkal.transact` with `externalActionData.externalActionId` set to the `DepositOnChainUtxosExternalAction` action, `erc20TokenAddresses = [T]`, `deltaAmounts[i] = 0`, and `externalActionMetadata` encoding `utxoAmounts = [[600]]`.
3. Attacker sets `circomData.originalSender = V` — a value never checked against `msg.sender` and never included in `getSignedMessageHash`, so the proof remains valid regardless of this field's contents.
4. `DepositOnChainUtxosExternalAction.runAction` executes `transferERC20TokenFrom(T, V, msg.sender, 600)`, pulling 600 tokens from `V`'s wallet using the leftover allowance, and creates shielded UTXOs worth 600 `T` for attacker `A`'s stealth address [7](#0-6) .
5. `V` has lost 600 `T` with no signature or proof knowledge on their part; `A` now controls shielded UTXOs of that value.

### Citations

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L31-82)
```text
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
```

**File:** contracts/CircomDataBuilder.sol (L97-132)
```text
    function getSignedMessageHash(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256 emporiumMessage
    ) internal pure returns (uint256) {
        // split into two encode calls to avoid "stack too deep"
        uint256 hash1 = uint256(
            keccak256(
                abi.encode(
                    chainId,
                    verifyingContract,
                    circomData.rootHashHinkal,
                    _encodeTokenAddresses(circomData.erc20TokenAddresses),
                    _encodeAmountChanges(circomData.amountChanges),
                    circomData.timeStamp,
                    _flatUint256Matrix(circomData.inputNullifiers),
                    _flatUint256Matrix(circomData.outCommitments),
                    circomData.calldataHash,
                    emporiumMessage
                )
            )
        );
        uint256 hash2 = uint256(
            keccak256(
                abi.encode(
                    circomData.stealthAddressStructure.H1x,
                    circomData.stealthAddressStructure.H1y,
                    circomData.stealthAddressStructure.H0x,
                    circomData.stealthAddressStructure.H0y
                )
            )
        );
        return
            uint256(keccak256(abi.encode(hash1, hash2))) % CIRCOM_P;
    }
```

**File:** contracts/CircomDataBuilder.sol (L163-210)
```text
    function formInputNormal(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);
        uint16 index = 0;
        input = formBasicInput(
            chainId,
            verifyingContract,
            circomData,
            input,
            index,
            circomData.emporiumMessage
        );
    }

    function formBasicInput(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256[] memory input,
        uint256 index,
        uint256 emporiumMessage
    ) internal pure returns (uint256[] memory) {
        // 1) First we list public inputs as in the body of the main template (not the one with exact dimensions)
        input[index++] = circomData.stealthAddressStructure.H1x;
        input[index++] = circomData.stealthAddressStructure.H1y;
        input[index++] = circomData.stealthAddressStructure.stealthAddress;
        input[index++] = emporiumMessage; // this is for Emporium message signature verification

        // 2) Then we list the private inputs as in the body of the main template
        input[index++] = circomData.rootHashHinkal;
        input[index++] = getSignedMessageHash(
            chainId,
            verifyingContract,
            circomData,
            emporiumMessage
        );

        for (uint16 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            input[index++] = uint256(
                uint160(circomData.erc20TokenAddresses[i])
            );
        }

        for (uint16 i = 0; i < circomData.amountChanges.length; i++) {
            require(
```

**File:** contracts/Transferer.sol (L74-81)
```text
    function transferERC20TokenFrom(
        address _erc20TokenAddress,
        address _from,
        address _to,
        uint256 _value
    ) internal {
        IERC20(_erc20TokenAddress).safeTransferFrom(_from, _to, _value);
    }
```
