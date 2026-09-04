## Finding

### Title
Emporium relay-fee token and recipient are not bound by the EIP-712 signer authorization, allowing theft of arbitrary wallet tokens — (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable` lets a smart-wallet owner authorize a batch of operations via an EIP-712 signature (`stack.signerAddress`), after which the contract is allowed to instruct the wallet (`IHinkalWallet`) to pay a relay fee via `doSendToRelay`. The signed payload never commits to the fee token or the fee recipient, so any unprivileged relayer/prover assembling the `CircomData` can redirect the fee to itself, denominated in any ERC-20 the wallet holds, while the on-chain check only compares raw numeric magnitudes.

### Finding Description
The EIP-712 typehash signed by the wallet owner is: [1](#0-0) 

It covers only `message` (`emporiumMessage`), the hash of `ops` (`endpoint`, `invokeWallet`, `value`, `callData`), `maxFee`, and `deadline`: [2](#0-1) 

The only fee-related check derived from the signature is that `flatFee` doesn't exceed the signed `maxFee`: [3](#0-2) 

Neither `circomData.feeStructure.feeToken` nor `circomData.relay` is part of the signed EIP-712 message, `EMPORIUM_SIGNATURE_TYPEHASH`, or any nullifier/commitment binding. They are also not part of the private-key-authenticated `signedMessageHash` used by the ZK circuit — that hash is built from `rootHashHinkal`, `erc20TokenAddresses`, `amountChanges`, `timeStamp`, nullifiers, commitments, `calldataHash`, and `emporiumMessage` [4](#0-3) , but that hash authenticates the *shielded-note owner's* spend, not the *wallet's* consent to a fee token/recipient chosen by the relay for the Emporium op. `circomData` (including `feeStructure` and `relay`) is instead supplied and hashed into `calldataHash` by whoever submits `transact()` — i.e., the relay/prover, not necessarily `stack.signerAddress` [5](#0-4) .

`payRelayFees` then unconditionally instructs the wallet to send `flatFee` units of `feeStructure.feeToken` to `circomData.relay`, even when that token is not among the tokens actually being moved by the operation (`!foundToken` branch): [6](#0-5) 

The wallet call itself is unconditional and trusts the caller-supplied token/recipient: [7](#0-6) 

Because `flatFee` is a raw `uint256` with no token binding, `flatFee <= maxFee` is a purely numeric check. A relay can set `feeStructure.feeToken` to any high-value token the wallet holds and `circomData.relay` to its own address, then satisfy `flatFee <= maxFee` trivially (e.g. the user signed `maxFee = 1e6` expecting 1 USDC, but the relay charges 1e6 units of an 18-decimal or higher-value token instead), extracting far more value than the user authorized — and to a recipient the user never authorized at all.

### Impact Explanation
This breaks the equality that a signer's EIP-712 authorization should fully constrain any funds moved out of their wallet. An unprivileged relay/prover can move wallet-held ERC-20 tokens to itself under the guise of a "relay fee," in a token and amount magnitude the signer never approved. This is direct theft of user funds from the smart wallet by an entity that only needed to observe/relay a legitimately signed op — no additional wallet-owner or prover key compromise is required.

### Likelihood Explanation
Any relay operator who processes a signed Emporium message can trigger this: they already control the surrounding `CircomData` (including `feeStructure` and `relay`) and only need a valid signature over the fixed, narrow typehash fields (`message`, `ops`, `maxFee`, `deadline`), which they normally receive as part of relaying the user's request in the honest flow. No special privilege is required beyond standard relay/prover capability.

### Recommendation
Bind `feeStructure.feeToken` (and ideally `circomData.relay`, or at least restrict it to a registered relay set) into the EIP-712 `EMPORIUM_SIGNATURE_TYPEHASH` so the signer explicitly authorizes both the fee token and the fee recipient, not just a token-agnostic numeric cap. Alternatively, require `feeStructure.feeToken` to be a token already present in `erc20TokenAddresses` with a bounded `deltaAmountChanges` entry, and validate the relay fee value against a price/exchange-rate the signer actually approved rather than a raw magnitude comparison.

### Proof of Concept
1. Wallet owner authorizes an Emporium message expecting to pay `maxFee = 1_000_000` (intending 1 USDC, 6 decimals) as `feeStructure.feeToken = USDC`, signing only `(emporiumMessage, opsHash, maxFee, deadline)`.
2. A relay intercepts the broadcasted signed payload (or otherwise obtains it through the normal relay flow) and builds its own `CircomData`/proof for `transact()`, setting `circomData.feeStructure = {feeToken: WBTC, flatFee: 1_000_000, variableRate: 0}` and `circomData.relay = attacker`.
3. `verifyWallet` only checks `flatFee (1_000_000) <= maxFee (1_000_000)` — passes — and validates the ops/message/deadline signature, all of which are unaffected by the fee-token/relay change.
4. `payRelayFees` calls `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(attacker, 1_000_000, WBTC)`, transferring 1,000,000 units of WBTC (an 8-decimal token worth orders of magnitude more than 1 USDC) from the wallet to the attacker.

Note: I could not inspect the concrete `IHinkalWallet`/`doSendToRelay` implementation in this pass to confirm it performs no independent token/amount sanity check beyond what Emporium instructs; if such a check exists there, it should be verified, but nothing in `EmporiumUpgradeable.sol` or the `CircomData`/EIP-712 scope constrains `feeToken`/`relay` to the signer's intent.

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-260)
```text
    function payRelayFees(
        CircomData calldata circomData,
        address signerAddress,
        int256[] calldata deltaAmountChanges
    ) internal {
        FeeStructure calldata feeStructure = circomData.feeStructure;

        bool foundToken = false;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            // tokens deposited into Emporium are not charged
            if (deltaAmountChanges[i] >= 0) {
                continue;
            }

            address erc20TokenAddress = circomData.erc20TokenAddresses[i];
            bool isFeeToken = erc20TokenAddress == feeStructure.feeToken;

            if (isFeeToken) {
                foundToken = true;
            }

            uint256 relayFee = 0;
            uint256 flatFee = isFeeToken ? feeStructure.flatFee : 0;

            if (signerAddress == address(0)) {
                uint256 sumAbs = uint256(-deltaAmountChanges[i]);

                EmporiumStorageVars storage $ = _getEmporiumStorage();
                relayFee = $._hinkalHelper.calculateRelayFee(
                    sumAbs,
                    flatFee,
                    feeStructure.variableRate
                );
            } else {
                relayFee = flatFee;
            }

            payRelay(
                circomData.relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }

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
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-335)
```text
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L346-348)
```text
        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
```

**File:** contracts/CircomDataBuilder.sol (L20-35)
```text
    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
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
