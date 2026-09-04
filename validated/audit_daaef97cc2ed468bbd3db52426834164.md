### Title
Unrestricted arbitrary call from `EmporiumUpgradeable` (`msg.sender == Emporium`) reachable via a proof-less Min-circuit "session" enables permanent token approvals to an attacker - (`File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`, circuit gate: `circuits/MainEVMCircuitMin.circom`)

### Summary
`EmporiumUpgradeable.runAction`'s CASE 2 branch performs `op.endpoint.call(op.callData)` with `msg.sender == Emporium` whenever `stack.signerAddress == address(0)`, with no allow-list on `op.endpoint`/`op.callData` beyond blocking the wallet-callback selectors. Because the `HINKAL_EMPORIUM_ACTION_ID` + zero-token-dimension path is verified with `MainEVMCircuitMin`, whose only constraint is `message <== Poseidon(1)([messageSeed])`, the `calldataHash` (and thus every field it commits to, including the entire `EmporiumStack`) is a public input that is never bound by any real circuit constraint to a nullifier, root hash, or signature. An attacker with zero prior deposits can therefore produce a self-consistent, always-valid proof and force Emporium to execute an arbitrary call, e.g. `token.approve(attackerSpender, type(uint256).max)`, as itself.

### Finding Description
The equality that should hold: *the set of addresses able to move tokens held by Emporium == addresses derived from an authenticated flow (a real signed `EmporiumStack` or wallet call originating from the token owner)*. After this exploit: *authorized-movers-of-Emporium-funds ⊇ {attackerSpender}* forever, independent of any subsequent depositor's consent.

Path:
- `Hinkal.transact` → `hinkalHelper.performHinkalChecks` [1](#0-0)  only checks `originalSender`/`relay` consistency, `getHashedCalldata(circomData) == circomData.calldataHash` (an internal self-consistency hash, not an ownership proof), `dimensionsCheck`, and `checkOnchainCreation` [2](#0-1) . None of these validate that the caller owns any UTXO or balance.
- `dimensionsCheck` merely requires `circomData.erc20TokenAddresses.length == dimensions.tokenNumber`; `tokenNumber = 0` is accepted [3](#0-2) , which routes `formInputForCircom` to `formInputEmporiumMin` [4](#0-3) , selecting the `MainEVMCircuitMin` verifier.
- `MainEVMCircuitMin` only constrains `message <== Poseidon(1)([messageSeed])`; `outTimeStamp` and `calldataHash` are declared public inputs but appear in **no constraint** [5](#0-4) . There is no root-hash check, no nullifier, no EdDSA signature, no `OverflowPreventer`/amount check anywhere in this path. Any `calldataHash` (hence any `externalActionMetadata`/`EmporiumStack`) can be freely chosen by the attacker and a valid Groth16 proof trivially produced.
- `_externalTransact` then calls `EmporiumUpgradeable.runAction(circomData, deltaAmountChanges)` with `deltaAmountChanges` of length 0 (since `erc20TokenAddresses.length == 0`) [6](#0-5) .
- Inside `runAction`, `verifyWallet` returns immediately when `stack.signerAddress == address(0)` (only marking `usedMessages`) [7](#0-6) , so **no signature check at all** is required for CASE 2.
- CASE 2 executes `op.endpoint.call{value: op.value}(op.callData)` for any `endpoint`/`callData` other than the two blocked wallet selectors [8](#0-7) , with `msg.sender == address(Emporium)`.
- Setting `endpoint = token`, `callData = abi.encodeCall(IERC20.approve, (attackerSpender, type(uint256).max))` grants a persistent, protocol-level ERC20 approval from Emporium to the attacker, entirely independent of the balance-consistency loop that follows (`balancesAfter - balancesBefore` only governs UTXO issuance, not the validity of side-effect calls already executed).

No existing guard (`performHinkalChecks`, `dimensionsCheck`, `verifyProof`/`buildVerifierId`, `rootHashExists`, `insertNullifiers`, `onlyAllowedRecipient`, `verifyWallet`, `OverflowPreventer`) constrains `op.endpoint`/`op.callData` when `signerAddress == 0`, nor does the Min circuit bind `calldataHash` to any real fund ownership.

### Impact Explanation
Any future ERC20 balance that legitimately transits Emporium (e.g., a normal user's deposit-then-swap session, or any external action leaving intermediate balance in Emporium) becomes pullable by `attackerSpender` via `transferFrom(emporium, attacker, amount)` at any later block, entirely outside of `transact()`'s own accounting. This is direct theft of in-flight/protocol-held user funds with no bound on repeatability (the attacker can install approvals for every ERC20 the protocol supports), matching the **Critical** category (direct theft of in-flight user funds via a call the wallet owner/prover never authorized).

### Likelihood Explanation
No preconditions beyond Emporium and `VerifierEVMMin0v4` being registered (which they are, by design, to support gas-less/proof-less style flows). The attacker needs no deposit, no nullifier, no balance — only the ability to call `Hinkal.transact` with `originalSender == msg.sender` and `relay == address(0)` (self-relayed, permitted by `performHinkalChecks`), and to generate a valid proof for `MainEVMCircuitMin`, which is trivial since its only real constraint is a self-chosen Poseidon preimage. This is a single, cheap, fully repeatable transaction requiring only gas.

### Recommendation
Remove or gate the fully-open CASE 2 arbitrary-call path: bind `op.endpoint`/`op.callData` to a real proof of ownership/authorization (e.g., always require `stack.signerAddress != address(0)` with a verified EIP-712 signature, or restrict CASE 2 endpoints to an explicit allow-list of known integrations), and add real constraints to `MainEVMCircuitMin` (or retire the Min circuit entirely) so `calldataHash` is cryptographically tied to a spent/authenticated UTXO rather than being a free public input.

### Proof of Concept
Foundry test outline:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register `VerifierEVMMin0v4` for the zero-token dimension and `HINKAL_EMPORIUM_ACTION_ID` for Emporium.
2. As `attacker`, build `CircomData` with `erc20TokenAddresses = []`, `originalSender = attacker`, `relay = address(0)`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.approve,(attackerSpender, type(uint256).max))})], ...}))`.
3. Set `calldataHash = getHashedCalldata(circomData)` and locally generate a valid Groth16 proof for `MainEVMCircuitMin` using an arbitrary `messageSeed` (no real deposit/UTXO needed).
4. Call `hinkal.transact(a,b,c,dimensions,circomData)` — assert it succeeds and `token.allowance(emporium, attackerSpender) == type(uint256).max`.
5. Separately, simulate a legitimate victim depositing/transiting `amount` of `token` through Emporium mid-flow so `token.balanceOf(emporium) >= amount`.
6. From `attackerSpender`, call `token.transferFrom(emporium, attacker, amount)` and assert success, demonstrating theft of the victim's in-flight funds.

### Citations

**File:** contracts/Hinkal.sol (L30-56)
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
```

**File:** contracts/Hinkal.sol (L234-261)
```text
    function _externalTransact(
        CircomData calldata circomData
    ) internal returns (UTXO[] memory) {
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );

        int256[] memory deltaAmountChanges = new int256[](
            circomData.erc20TokenAddresses.length
        );
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            deltaAmountChanges[i] = _calculateDeltaAmount(circomData, i);
            if (deltaAmountChanges[i] < 0) {
                transferERC20TokenOrETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    uint256(-deltaAmountChanges[i])
                );
            }
        }

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
    }
```

**File:** contracts/HinkalHelper.sol (L64-76)
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

```

**File:** contracts/HinkalHelper.sol (L204-236)
```text
    ///@notice make performance checks for transactions
    ///@dev Check if transacaction is valid before making it
    ///@param circomData circom data
    ///@return inputForCircom
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-118)
```text
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
