### Title
Emporium min-circuit path lets any caller run signature-free, unaccounted `EmporiumStack` ops that drain Emporium's ERC20/ETH balances - (File: contracts/CircomDataBuilder.sol, contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, whose circuit (`MainEVMCircuitMin.circom`) only proves knowledge of a self-chosen `messageSeed` and constrains nothing about the `EmporiumStack` contents. Combined with `EmporiumUpgradeable.runAction`'s `verifyWallet` skipping all ECDSA verification when `stack.signerAddress == address(0)`, and its balance-accounting loop operating over the (attacker-supplied, empty) `erc20TokenAddresses` array, an unprivileged caller can execute arbitrary `EmporiumOperation`s from Emporium's own address with zero authorization and zero accounting, draining any tokens/ETH held by the contract.

### Finding Description
The invariant that should hold is: *every token balance Emporium can move in a transaction is accounted for in `balancesBefore`/`balancesAfter`, and every op executed is authorized either by a valid `signerAddress` signature or by a ZK proof that actually constrains the op contents.* Both halves of this invariant are broken on the min-circuit path.

**Broken proof binding.** `formInputForCircom` selects the minimal input set whenever the emporium action is used with an empty token array: [1](#0-0) 
`formInputEmporiumMin` produces only `emporiumMessage`, `timeStamp`, `calldataHash` as public inputs: [2](#0-1) 
The matching circuit `MainEVMCircuitMin.circom` constrains nothing except `message == Poseidon(messageSeed)`, where `messageSeed` is a private input chosen entirely by the prover — there is no linkage of this proof to any UTXO ownership, nullifier, or the actual `EmporiumStack`/ops being executed: [3](#0-2) 
The on-chain `calldataHash` consistency check in `performHinkalChecks` (`getHashedCalldata(circomData) == circomData.calldataHash`) is not a security control against a malicious caller — the attacker computes this hash themselves over data they fully control, so it only guarantees self-consistency, not authorization: [4](#0-3) 

**Broken signature check.** `EmporiumUpgradeable.runAction` decodes the attacker-supplied `EmporiumStack` straight from `externalActionMetadata`: [5](#0-4) 
`verifyWallet` returns immediately, skipping the entire EIP-712 signature-recovery block, whenever `stack.signerAddress == address(0)`: [6](#0-5) 

**Broken accounting.** The ops loop executes arbitrary calls to `op.endpoint` with attacker-chosen `callData`/`value` (the "Stateless Interaction" branch only blocks the `callHinkalWallet`/`doSendToRelay` selectors, nothing else): [7](#0-6) 
Balance accounting is only performed over `circomData.erc20TokenAddresses`, which is empty in the min path, so `balancesBefore`/`balancesAfter` are empty arrays and the reconciliation loop (which would normally revert on `balanceChange < 0`) never runs for any token actually moved by the ops: [8](#0-7) 

**Exploit flow.** An unprivileged EOA:
1. Generates a trivial proof for `MainEVMCircuitMin` (self-chosen `messageSeed`, no secret needed).
2. Calls `Hinkal.transact` with `circomData.externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `circomData.erc20TokenAddresses = []`, and `externalActionMetadata` encoding an `EmporiumStack` with `signerAddress = address(0)` and an `ops` array containing e.g. `{endpoint: <ERC20 token held by Emporium>, callData: transfer(attacker, allEmporiumBalance)}`, or `{endpoint: <attacker-controlled LiFi-style router>, callData: <arbitrary swap/drain calldata>}`.
3. `performHinkalChecks` passes (self-consistent hash, trivially satisfied relay/dimension checks for an empty-array transaction).
4. Hinkal (an allowed recipient) invokes `EmporiumUpgradeable.runAction`, `verifyWallet` no-ops on `signerAddress == 0`, and the ops execute directly from Emporium's identity, transferring out any ERC20/ETH balance Emporium holds (e.g. funds parked mid-swap for other users, or leftover approvals/balances).
5. No `balancesBefore`/`balancesAfter` mismatch is ever raised because `erc20TokenAddresses` is empty, so the theft is invisible to the accounting guard.

Existing guards fail because: `performHinkalChecks`'s `calldataHash` check is only an internal-consistency check controlled by the attacker; `dimensionsCheck`/`checkOnchainCreation` do not constrain `externalActionMetadata` contents; the circuit itself (min path) constrains nothing relevant; and `verifyWallet`'s `signerAddress == address(0)` branch was evidently intended for a different trust model (e.g., relay-initiated ops) but is reachable directly by any caller in the min path with no relay privilege enforced at this point.

### Impact Explanation
An attacker can steal any ERC20 token balance or ETH held by the `EmporiumUpgradeable` contract — this includes funds "parked" there in flight for other users (e.g., mid-swap balances, un-relayed deposits) — with a single transaction requiring no real proof secret and no valid signature. This matches Critical: "direct theft of shielded or in-flight user funds." The attack is repeatable for every token/asset balance Emporium accumulates and costs the attacker only gas plus a freely-generatable proof.

### Likelihood Explanation
Preconditions are minimal: the attacker needs no special role, no valid UTXO, and no signature — only the ability to call `Hinkal.transact` (available to any unprivileged EOA per the threat model) and the ability to craft `CircomData`/`externalActionMetadata`, both explicitly listed as attacker capabilities. The only requirement is that Emporium hold a non-zero balance of some asset at the time of the call, which is a normal operating condition for a contract that "parks" balances during multi-step actions. Feasibility is high and the exploit is trivially repeatable.

### Recommendation
- Remove or gate the `signerAddress == address(0)` bypass in `verifyWallet`; every op execution must require either a valid EIP-712 signature or a ZK proof whose public inputs actually constrain the operation list (endpoints, calldata, values) and, ideally, the `erc20TokenAddresses`/`amountChanges` used for accounting.
- Do not allow `formInputEmporiumMin` to be selected merely by supplying an empty `erc20TokenAddresses` array while permitting an arbitrary, unconstrained `EmporiumOperation[]` in the same call; bind the op list (via hash) into the circuit's public inputs regardless of path, and require the circuit to constrain `signerAddress`/authorization.
- Ensure Emporium's balance accounting cannot be trivially bypassed by supplying an empty token array — e.g., compute `balancesBefore`/`balancesAfter` based on a token set derived from the ops themselves, or forbid `erc20TokenAddresses.length == 0` when `ops.length > 0`.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, fund it with e.g. 1000 USDC (simulating parked balance from another user's in-flight action).
2. Deploy `Hinkal` wired to the real `MainEVMCircuitMin` verifier; as attacker EOA, generate a valid proof for `MainEVMCircuitMin` using a self-chosen `messageSeed` (no dependency on any real secret).
3. Construct `CircomData` with `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, `amountChanges = []`, and `externalActionMetadata` ABI-encoding an `EmporiumStack{ signerAddress: address(0), ops: [ EmporiumOperation{ endpoint: address(USDC), invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 1000e6)) } ], maxFee: 0, deadline: block.timestamp }`.
4. Call `Hinkal.transact(circomData, dimensions, proof)` from the attacker EOA.
5. Assert: `USDC.balanceOf(attacker)` increased by 1000e6, `USDC.balanceOf(Emporium)` decreased by 1000e6, and no revert occurred in the `balancesBefore`/`balancesAfter` reconciliation loop (confirming the equality "assets moved == assets accounted" is violated: assets moved = 1000e6, assets accounted = 0 since `erc20TokenAddresses.length == 0`).

### Citations

**File:** contracts/CircomDataBuilder.sol (L139-148)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-83)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-118)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-151)
```text
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
