### Title
Emporium "min-proof" path lets any unprivileged caller drive `EmporiumUpgradeable.runAction` with a self-signed, unauthenticated `EmporiumStack` and zero balance accounting, draining any funds parked on the Emporium contract, replayable on every chain where Emporium is deployed — ([File: contracts/CircomDataBuilder.sol], [File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes proof verification to `formInputEmporiumMin`, whose backing circuit `MainEVMCircuitMin` proves nothing except that the prover knows *some* preimage of the public `message` signal — a fact any attacker can trivially satisfy for a value they invented themselves. Combined with `signerAddress == address(0)` skipping signature verification in `verifyWallet`, and `erc20TokenAddresses.length == 0` making every balance-accounting loop in both `Hinkal.transact` and `EmporiumUpgradeable.runAction` a no-op, an attacker can submit an arbitrary `EmporiumStack.ops` array that is executed with Emporium's own identity as `msg.sender`, transferring out any ERC20/ETH balance parked on the Emporium contract with no economic check at all.

### Finding Description
The invariant that should hold is: *assets Emporium can move in a transaction == assets accounted for in `balancesBefore`/`balancesAfter`*. This is broken because the accounting arrays are sized by `circomData.erc20TokenAddresses.length`, which the attacker sets to `0`.

- `formInputForCircom` selects the minimal proof path whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`: [1](#0-0) 
- The circuit behind this path, `MainEVMCircuitMin`, only constrains `message <== Poseidon(1)([messageSeed])` where `messageSeed` is a private input fully chosen by the prover — it encodes no UTXO ownership, no signer identity, and no economic binding whatsoever: [2](#0-1) 
- `dimensionsCheck` is satisfied trivially because every array (`amountChanges`, `inputNullifiers`, `outCommitments`, `onChainCreation`, `slippageValues`, `encryptedOutputs`) is required to have length `0` to match `tokenNumber == 0`: [3](#0-2) 
- `Hinkal._externalTransact` builds `deltaAmountChanges` sized to `erc20TokenAddresses.length` (i.e. empty), so no pre-transfer occurs, and calls `IExternalActionV2.runAction`: [4](#0-3) 
- `EmporiumUpgradeable.runAction` decodes the attacker-supplied `EmporiumStack` from `externalActionMetadata`, computes `balancesBefore`/`balancesAfter` only over the (empty) `erc20TokenAddresses` array, calls `verifyWallet`, then executes every `op` in `stack.ops`: [5](#0-4) 
- `verifyWallet` returns immediately, skipping all ECDSA signature checks, whenever `stack.signerAddress == address(0)`: [6](#0-5) 
- With `signerAddress == 0`, each `op` falls into the "stateless" branch and is executed as `op.endpoint.call{value: op.value}(op.callData)` directly from Emporium's own address, blocked only from calling `callHinkalWallet`/`doSendToRelay` selectors — nothing stops calling an ERC20's `transfer` selector: [7](#0-6) 
- Because `circomData.erc20TokenAddresses.length == 0`, the post-loop accounting/UTXO-creation loop is empty and never observes or reverts on the balance change performed by the op: [8](#0-7) 

The attacker's exact call is `Hinkal.transact(a,b,c, dimensions{0,0,0}, circomData)` with:
- `erc20TokenAddresses = []`, all dimension-tied arrays empty, `rootHashHinkal` any valid historical root (unconstrained by the min circuit),
- `externalActionData = {externalAddress: <Emporium>, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: victimToken, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, balanceOf(Emporium)))}], maxFee: 0, deadline: MAX})}`,
- a locally-generated Groth16 proof for `MainEVMCircuitMin` with a self-chosen `messageSeed`.

`calldataHash` correctly binds `externalActionMetadata` (checked in `performHinkalChecks` via `getHashedCalldata`), but this only proves the attacker didn't tamper with their own calldata in flight — it does not authorize anything, since the calldata itself is entirely attacker-authored and requires no permission from Emporium's owner, a signer, or any UTXO owner.

Additionally, unlike the normal path's `getSignedMessageHash` (which binds `chainId` and `verifyingContract`), `formInputEmporiumMin`'s public inputs (`emporiumMessage`, `timeStamp`, `calldataHash`) contain no chain identifier, so the identical `(a,b,c)` proof and calldata is valid on every chain where an equivalent `mainEVMCircuitMin` verifier is registered and Emporium holds funds (e.g. Base and Arbitrum), letting the attacker replay the exact same drain transaction on each deployment.

### Impact Explanation
Any funds held by the Emporium contract (parked ERC20 tokens or ETH from in-flight multi-step flows, accrued relay fees, or residual balances) can be transferred out by an unprivileged attacker with a single self-authored proof and no signature, matching **Critical: direct theft of shielded or in-flight user funds**. The attack is repeatable per unused `emporiumMessage` nonce and, because the min-circuit's public inputs are not chain-bound, is directly replayable across every chain hosting an Emporium instance with the same registered verifier.

### Likelihood Explanation
Preconditions are minimal and fully attacker-controlled: no privileged role, no valid signature, and no real UTXO ownership are required. The only requirements are that Emporium holds a non-zero balance of some token and that a min-circuit verifier is registered for `tokenNumber == 0` combined with `HINKAL_EMPORIUM_ACTION_ID` (evidenced by the deployed `mainEVMCircuitMin0v4` verifier expecting exactly 3 public inputs). Cost is a single proof generation (trivial, self-chosen preimage) and gas. This is highly feasible and repeatable.

### Recommendation
- Bind `MainEVMCircuitMin`'s public inputs (and `formInputEmporiumMin`) to `chainId`/`verifyingContract` as `formBasicInput`/`getSignedMessageHash` already do for the normal path, to prevent cross-chain replay.
- Do not allow the min-proof path to skip signer authorization: require `stack.signerAddress != address(0)` (i.e. a valid EIP-712 signature) whenever `stack.ops` performs stateless calls that can move Emporium's own funds, or otherwise cryptographically bind the `ops` to a real, checked authority (owner, signer, or UTXO-derived key) rather than an arbitrary self-chosen `messageSeed`.
- Track and enforce actual balance deltas for tokens touched by arbitrary `op.endpoint.call` targets even when `erc20TokenAddresses` is empty, e.g. by disallowing stateless calls to arbitrary `endpoint` addresses that are not part of a pre-approved allowlist of DeFi routers/hooks, or by requiring `erc20TokenAddresses`/accounting arrays to cover every token that could be affected by `stack.ops`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `VerifierFacade`, register a `mainEVMCircuitMin0v4`-based verifier under `buildVerifierId(Dimensions(0,0,0), HINKAL_EMPORIUM_ACTION_ID)`.
2. Deploy `EmporiumUpgradeable`, register it via `Hinkal.registerExternalAction(HINKAL_EMPORIUM_ACTION_ID, emporium)`, add `Hinkal` as an allowed recipient.
3. Fund `emporium` with `1000e18` of a mock ERC20 (`victimToken`) to simulate parked balance.
4. As `attacker` (no special role), build `EmporiumStack{signerAddress: address(0), ops: [{endpoint: victimToken, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 1000e18))}], maxFee: 0, deadline: type(uint256).max}`.
5. Build `circomData` with `erc20TokenAddresses = []`, all dimension arrays empty, correct `calldataHash`, a fresh `emporiumMessage`, and `rootHashHinkal` set to any existing valid root/index.
6. Generate a real Groth16 proof for `MainEVMCircuitMin` with a self-chosen `messageSeed` such that `Poseidon(messageSeed) == emporiumMessage`.
7. Call `Hinkal.transact(a,b,c, Dimensions(0,0,0), circomData)` from `attacker`.
8. Assert: `victimToken.balanceOf(emporium)` goes from `1000e18` to `0`, and `victimToken.balanceOf(attacker)` increases by `1000e18` — i.e. `balancesBefore == balancesAfter` (both empty arrays, never violated) while the actual on-chain token balance was fully drained, proving the accounting invariant is broken.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-118)
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
