This confirms the analysis. `EmporiumStack` [1](#0-0)  only contains `v,r,s,signerAddress,ops,maxFee,deadline` — `feeStructure`, `relay`, `erc20TokenAddresses`, `stealthAddressStructure` live in the separately-supplied, unsigned `CircomData` [2](#0-1) , and `EMPORIUM_SIGNATURE_TYPEHASH` binds only `(ops, maxFee, deadline, emporiumMessage)` [3](#0-2) .

### Title
Wallet-owner's `flatFee` can be redirected to an attacker-chosen relay via unsigned `CircomData` fields - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`verifyWallet` only authenticates `(ops, maxFee, deadline, emporiumMessage)` from a harvested `EmporiumStack` signature, but `payRelayFees` pulls up to `stack.maxFee` worth of `feeStructure.feeToken` directly from the signer's `HinkalWallet` and sends it to `circomData.relay` — both of which are attacker-controlled, unsigned fields supplied in the surrounding `CircomData`. An attacker who obtains any valid signed `EmporiumStack` (via mempool, dropped tx, or relay quote) can wrap it in their own `CircomData`/proof and drain `flatFee` (bounded by `maxFee`) of an arbitrary token from the wallet owner's `HinkalWallet` to themselves.

### Finding Description
The broken equality: the wallet owner's signature authorizes `(ops, maxFee, deadline, emporiumMessage)`, and the intent is that "the fee paid from the wallet == the fee/token/relay the owner implicitly agreed to when signing maxFee". In reality, `(feeStructure.feeToken, feeStructure.flatFee ≤ maxFee, relay)` are free-form fields in `CircomData` never covered by `EMPORIUM_SIGNATURE_TYPEHASH` [4](#0-3) .

Call path: `Hinkal.transact` → `Hinkal._externalTransact` → `EmporiumUpgradeable.runAction` → `verifyWallet(stack, circomData)` (only checks the ops/maxFee/deadline signature and `usedMessages`) [5](#0-4)  → op execution → `payRelayFees(circomData, stack.signerAddress, deltaAmountChanges)`.

In `payRelayFees`, when the fee token is *not* present in `circomData.erc20TokenAddresses` (`foundToken == false`) but `feeStructure.flatFee != 0`, the contract unconditionally calls `payRelay(circomData.relay, signerAddress, feeStructure.flatFee, feeStructure.feeToken)` as long as `signerAddress != address(0)` [6](#0-5) . `payRelay` then routes through `sendToRelayFromWallet`, which calls `IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, feeToken)` [7](#0-6) , pulling `feeToken` directly out of the wallet owner's `HinkalWallet` contract balance and sending it to `relay`.

The only constraint tying `feeStructure.flatFee` to the signature is `require(circomData.feeStructure.flatFee > stack.maxFee)` revert in `verifyWallet` (i.e. `flatFee ≤ maxFee`) [8](#0-7) . Nothing constrains `feeStructure.feeToken` or `circomData.relay`, and `stack.ops` (the only signed part) need not reference the drained token at all — an attacker can attach any (unrelated, even no-op) `ops` array as long as it matches what was signed, then freely choose `feeToken`/`relay`/`flatFee` up to `maxFee`.

Because the attacker generates their own ZK proof over their own UTXOs/`CircomData`, `verifyProof`/`calldataHash`/`signedMessageHash` (`getSignedMessageHash` in `CircomDataBuilder.sol` [9](#0-8) ) only bind the proof to the attacker's own chosen `CircomData` — they do not re-validate that `feeStructure`/`relay` match anything the wallet owner authorized, since that data was never part of the EIP-712 message signed by the wallet owner. `verifyWallet` recovers `signerAddress` correctly and passes, `usedMessages[emporiumMessage]` is fresh, so the whole path succeeds.

### Impact Explanation
An attacker can drain up to `stack.maxFee` of an arbitrary ERC20 (or ETH) held by the victim wallet owner's `HinkalWallet` to a relay address the attacker controls, per harvested signature. This is direct theft of the wallet owner's in-protocol funds (funds custodied by their `HinkalWallet`) executed via a call the wallet owner never authorized (they authorized `ops`/`maxFee`/`deadline`, not an arbitrary fee-token drain to an arbitrary relay). This is repeatable for every harvested/leaked `EmporiumStack` signature the attacker can find (e.g., broadcast-but-unmined relay transactions, or signatures obtained via relay quoting flows), up to the `maxFee` bound each time (and unlimited if a wallet owner signs a large `maxFee` intending it only for legitimate relay compensation of a specific action).

### Likelihood Explanation
Preconditions: attacker needs one previously-signed, not-yet-consumed `EmporiumStack` (obtainable from mempool, a relay quoting protocol, or a reverted/dropped transaction) — a realistic scenario since relayed meta-tx flows commonly expose signed messages before execution. No privileged role is required; attacker only needs to submit their own deposit/proof via `Hinkal.transact`, entirely within an unprivileged EOA's capabilities. The exploit is deterministic and cheap (one transaction, gas cost only).

### Recommendation
Include `feeStructure.feeToken`, `circomData.relay`, and any other economically-relevant fields (or at minimum a hash/commitment of the full intended `CircomData`/fee context) in `EMPORIUM_SIGNATURE_TYPEHASH` so the wallet owner's signature commits to exactly which token/relay may be charged, not just a numeric cap. Alternatively, require `feeStructure.feeToken` and `circomData.relay` to be passed as explicit fields inside the signed `EmporiumStack`/ops payload rather than sourced from the surrounding unsigned `CircomData`.

### Proof of Concept
Foundry test:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, a `HinkalWallet` funded with token `T` for victim `signerAddress`.
2. Victim signs `EmporiumStack{ops: [benign no-op or unrelated op], maxFee: M, deadline, signerAddress}` producing `(v,r,s)`.
3. Attacker deposits/creates a valid proof for their own UTXO set and builds `CircomData` with `feeStructure = {feeToken: T, flatFee: M, variableRate:0}`, `relay = attackerAddr`, `erc20TokenAddresses` not containing `T` (so `foundToken=false`), `externalActionData.externalActionMetadata = abi.encode(stack)`.
4. Call `Hinkal.transact(...)` → assert `runAction` succeeds, `verifyWallet` passes, and after the call `T.balanceOf(attackerAddr)` increased by `M` while `T.balanceOf(HinkalWallet)` decreased by `M`.
5. Assert this occurred despite the wallet owner never having signed anything referencing `T` or `attackerAddr` — i.e., assert the equality "(feeToken, relay) paid == (feeToken, relay) the owner intended" fails, by re-running the same signature with a second, honest `CircomData` (different `feeToken`/`relay`) that also passes `verifyWallet`, demonstrating two divergent outcomes (`AUTHORITY` fails) from one signature.

### Citations

**File:** contracts/external-actions/emporium/EmporiumStack.sol (L4-19)
```text
struct EmporiumOperation {
    address endpoint;
    bool invokeWallet;
    uint128 value;
    bytes callData;
}

struct EmporiumStack {
    uint8 v;
    bytes32 r;
    bytes32 s;
    address signerAddress;
    EmporiumOperation[] ops;
    uint256 maxFee;
    uint256 deadline;
}
```

**File:** contracts/types/CircomData.sol (L23-44)
```text
struct CircomData {
    uint256 rootHashHinkal;
    uint256 rootHashHinkalIndex;
    address[] erc20TokenAddresses;
    int256[] amountChanges;
    uint256[][] inputNullifiers;
    uint256[][] outCommitments;
    bytes[][] encryptedOutputs;
    bytes onChainEncryptedOutput;
    bool[] onChainCreation;
    int256[] slippageValues;
    FeeStructure feeStructure;
    StealthAddressStructure stealthAddressStructure;
    uint256 timeStamp;
    uint256 calldataHash;
    uint256 emporiumMessage;
    uint16 publicSignalCount;
    address relay;
    ExternalActionData externalActionData;
    HookData hookData;
    address originalSender;
    bytes extraData;
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L186-199)
```text
    function sendToRelayFromWallet(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address feeToken
    ) internal {
        if (relayFee > 0) {
            IHinkalWallet(signerAddress).doSendToRelay(
                relay,
                relayFee,
                feeToken
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L247-259)
```text
        if (!foundToken && feeStructure.flatFee != 0) {
            require(
                signerAddress != address(0),
                "Gas Token in Emporium is not found"
            );

            payRelay(
                circomData.relay,
                signerAddress,
                feeStructure.flatFee,
                feeStructure.feeToken
            );
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-349)
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

        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    EMPORIUM_SIGNATURE_TYPEHASH,
                    circomData.emporiumMessage,
                    _hashEmporiumOps(stack.ops),
                    stack.maxFee,
                    stack.deadline
                )
            )
        );

        (address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(
            hashedMessage,
            stack.v,
            stack.r,
            stack.s
        );
        bool verified = err == ECDSA.RecoverError.NoError &&
            recoveredAddress == stack.signerAddress;
        if (!verified) {
            revert InvalidSignature();
        }

        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
    }
```

**File:** contracts/CircomDataBuilder.sol (L97-119)
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
```
