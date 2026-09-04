## Title
Emporium wallet-mode relay fee lets the caller pick an unauthorised `feeToken` to drain arbitrary ERC-20 balances from `HinkalWallet` - (`File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
In the Emporium wallet flow, a signer authorises operations by EIP-712-signing `(emporiumMessage, ops, maxFee, deadline)`. `maxFee` is a bare `uint256` number that is never tied to a specific token. The actual token that gets pulled from the user's `HinkalWallet` as a "relay fee", `circomData.feeStructure.feeToken`, is chosen by whoever submits the transaction to `Hinkal` (an unprivileged relay/caller) and is never bound by the signer's signature nor by the ZK proof in this flow, allowing theft of any ERC-20 the wallet holds.

### Finding Description
Wallet-mode Emporium calls use `circomData.erc20TokenAddresses.length == 0`, which routes proof-input construction to the minimal circuit: [1](#0-0) 

This minimal circuit (`MainEVMCircuitMin`) only proves knowledge of a `messageSeed`; it carries no `spendingPublicKey`/EdDSA signature over `feeStructure`, unlike the normal flow: [2](#0-1) 

The only user-side authorisation left for wallet-mode transactions is the EIP-712 signature checked in `verifyWallet`, which covers `emporiumMessage`, the ops hash, `maxFee`, and `deadline` — but **not** `feeStructure.feeToken**: [3](#0-2) 

Because `circomData.erc20TokenAddresses.length == 0`, the loop in `payRelayFees` never executes, so `foundToken` stays `false` and the fallback branch always fires for wallet-mode calls with a non-zero flat fee, pulling `feeStructure.flatFee` of `feeStructure.feeToken` straight from the wallet: [4](#0-3) 

That path calls `doSendToRelay` on the user's `HinkalWallet`, which unconditionally transfers the requested token/amount to the relay once invoked by Emporium: [5](#0-4) 

Since `calldataHash` (which does include `feeStructure`, per `CircomDataBuilder.getHashedCalldata2`) is only a self-consistency check of the calldata against itself — not a check against anything the signer approved in this minimal-circuit path — an unprivileged caller (a malicious/compromised relay, or simply whoever assembles the transaction) can freely set `feeStructure.feeToken` to any ERC-20 the wallet holds and set `feeStructure.flatFee` up to the signed `maxFee` numeric value, regardless of that token's decimals or market value.

### Impact Explanation
This breaks the intended equality between "what the wallet owner authorised as a fee" and "what actually leaves the wallet": the signer only commits to a raw numeric ceiling (`maxFee`) with no token binding, while the relay unilaterally decides which token that ceiling applies to. A relay can therefore choose a high-value/low-decimal token present in the wallet and drain up to `maxFee` raw units of it as "fee," resulting in unauthorised asset movement/theft of wallet funds well beyond what the signer intended to pay. This is a wallet operation not authorised by the signer, matching the High-severity criterion "executing calls or moving assets a wallet owner ... never authorised."

### Likelihood Explanation
Any relay (or whoever crafts the `CircomData` submitted to `Hinkal.transact`) can trigger this deterministically for every wallet-mode Emporium call with a non-zero `flatFee`, since the vulnerable fallback branch is the *only* code path executed when `erc20TokenAddresses.length == 0` (always true for pure wallet interactions). No special privileges are required beyond being the relay/submitter, which in Hinkal's model is an untrusted third party.

### Recommendation
Bind `feeStructure.feeToken` (and ideally the full `feeStructure`) into the EIP-712 struct that `signerAddress` signs (`EMPORIUM_SIGNATURE_TYPEHASH`), so the wallet owner explicitly authorises both the fee token and the maximum amount in that token, rather than an ambiguous raw-number ceiling that can be reinterpreted against any token by the relay.

### Proof of Concept
1. User signs an Emporium `EmporiumSignature(message, ops, maxFee=1_000_000, deadline)` intending to pay at most 1 USDC (`maxFee` matches USDC's 6-decimal unit) in fees, with `erc20TokenAddresses = []` (pure wallet-mode call).
2. Relay submits `Hinkal.transact` with this signed stack but sets `circomData.feeStructure = {feeToken: WBTC, flatFee: 1_000_000, variableRate: 0}` and `circomData.erc20TokenAddresses = []`.
3. `performHinkalChecks` only re-hashes `circomData` against itself (`calldataHash`) — it succeeds because the relay is free to pick any `feeStructure` at submission time; the minimal circuit's proof doesn't constrain it either.
4. In `EmporiumUpgradeable.runAction`, `payRelayFees` loop is skipped (`erc20TokenAddresses.length == 0`), `foundToken` stays `false`, and since `flatFee != 0` and `signerAddress != address(0)`, it calls `payRelay(relay, signerAddress, 1_000_000, WBTC)`.
5. `sendToRelayFromWallet` → `HinkalWallet.doSendToRelay` transfers `1_000_000` units of WBTC (≈0.01 BTC, worth far more than 1 USDC) from the user's wallet to the relay — an amount and token the user never approved.

### Citations

**File:** contracts/CircomDataBuilder.sol (L139-161)
```text
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

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L36-42)
```text
    function doSendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) external onlyEmporium {
        sendToRelay(relay, actualAmount, erc20TokenAddress);
    }
```
