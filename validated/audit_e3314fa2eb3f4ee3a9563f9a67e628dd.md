### Title
Signature-less Emporium `runAction` allows arbitrary token drain unaccounted by balance checks - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
An unprivileged attacker can call `Hinkal.transact` with `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, which routes the call through `formInputEmporiumMin`, a circuit that only proves `message == Poseidon(messageSeed)` and constrains nothing about UTXOs, tokens, or the `EmporiumStack`. The attacker then supplies an `EmporiumStack` with `signerAddress == address(0)`, which skips all EIP-712 signature checks in `verifyWallet` and lets an arbitrary `op.endpoint.call(op.callData)` execute directly as the `Emporium` contract, e.g. `token.transfer(attacker, amount)`, draining tokens the Emporium contract holds while the empty `balancesBefore`/`balancesAfter` arrays never observe or revert on the change.

### Finding Description
The invariant that should hold is: **every asset that Emporium's `ops` loop can move in a transaction must be present in `circomData.erc20TokenAddresses` and reconciled by `balancesBefore`/`balancesAfter`.** This is broken because the `ops` execution loop is not bounded by, or related to, `erc20TokenAddresses.length` at all: [1](#0-0) 

- `formInputForCircom` routes to `formInputEmporiumMin` whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`: [2](#0-1) 

- `formInputEmporiumMin` produces only 3 public signals: `emporiumMessage`, `timeStamp`, `calldataHash`. The corresponding circuit, `MainEVMCircuitMin`, only constrains `message === Poseidon(messageSeed)`: [3](#0-2) 

Since `messageSeed` is attacker-chosen, the attacker trivially generates a valid proof for any `emporiumMessage` value they pick themselves — the proof carries no authorization about tokens, nullifiers, roots, or the `EmporiumStack` payload. `dimensionsCheck` further forces `amountChanges`, `inputNullifiers`, and `outCommitments` to be empty when `tokenNumber == 0`, so the attacker needs no owned UTXOs at all: [4](#0-3) 

- In `EmporiumUpgradeable.runAction`, `verifyWallet` returns immediately (skipping the EIP-712 signature check) when `stack.signerAddress == address(0)`: [5](#0-4) 

- With `signerAddress == address(0)`, every op falls to the "Stateless Interaction" branch, which lets the attacker specify `op.endpoint` and `op.callData` freely (only `callHinkalWallet`/`doSendToRelay` selectors are blocked), and the call is executed with `msg.sender == Emporium`: [6](#0-5) 

- Because `circomData.erc20TokenAddresses` is empty, `balancesBefore`/`balancesAfter` are empty arrays, and the reconciliation loop over `circomData.erc20TokenAddresses.length` never observes any balance change on the token targeted by the malicious op — no `BalanceChangeShouldBePositive` check ever fires for that token: [7](#0-6) 

- `Hinkal.transact`'s own balance accounting is likewise scoped to `circomData.erc20TokenAddresses`, so it is equally blind to the drained token: [8](#0-7) 

The attacker's call: `Hinkal.transact(a, b, c, dimensions{tokenNumber:0,...}, circomData{externalActionData:{externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalAddress: EmporiumAddress, externalActionMetadata: abi.encode(EmporiumStack{signerAddress:0, ops:[{endpoint: victimToken, invokeWallet:false, value:0, callData: transfer(attacker, balance)}], maxFee:0, deadline:0})}, erc20TokenAddresses: [], emporiumMessage: Poseidon(messageSeed), ...})` with a locally-generated `MainEVMCircuitMin` proof.

Additionally, `formInputEmporiumMin`'s public signals and `getHashedCalldata`'s inputs never include `chainId` (unlike `formBasicInput`'s `getSignedMessageHash`, which does bind to `chainId`/`verifyingContract`): [9](#0-8) 
This means the same calldata/proof pair is not chain-bound in the Min path, so if Emporium is deployed at the same address on two chains (e.g. Base and Arbitrum), the identical exploit payload can be sent to both, since `usedMessages` is tracked per-chain-deployment. This is a secondary aggravating factor; the core theft does not require replay since the attacker can freely mint a fresh `messageSeed`/`emporiumMessage` for every attack attempt.

### Impact Explanation
Any ERC20 token or ETH balance held by the `Emporium` contract — including funds momentarily in flight during a multi-step Emporium operation, or funds sent by the same or other users' relayed transactions before they are swept out — can be transferred to the attacker with zero accounting or authorization. This is direct theft of protocol/relay/in-flight user funds, matching the Critical severity category ("direct theft of shielded or in-flight user funds"). The attack is fully repeatable: each call only needs a fresh `messageSeed`, and `usedMessages` per-message replay protection does not prevent repeated exploitation with new messages.

### Likelihood Explanation
Preconditions are minimal and fully attacker-controlled: no owned UTXOs, no whitelisted role, no signature, and a trivially self-generated ZK proof for `MainEVMCircuitMin` (a single Poseidon constraint). The only requirement is that Emporium holds a nonzero token/ETH balance at call time, which occurs naturally as part of normal Emporium multi-step operations (funds deposited into Emporium before ops execute, or leftover dust from a prior op). Attacker cost is a single transaction plus proof generation; feasibility is high given the Min-path circuit imposes essentially no constraints.

### Recommendation
- Remove or gate the Min-proof shortcut so that `externalActionId == HINKAL_EMPORIUM_ACTION_ID` cannot bypass token/balance accounting: require `erc20TokenAddresses` to cover every token/ETH address touched by any `op.endpoint` in the `EmporiumStack`, or disallow `erc20TokenAddresses.length == 0` when `stack.ops.length > 0`.
- Do not allow `stack.signerAddress == address(0)` to skip signature verification for stateless ops that call arbitrary `op.endpoint`/`op.callData`; require an authenticated signer (or explicit protocol-controlled allowlist of endpoints) for any code path that can move Emporium's own funds.
- Bind `formInputEmporiumMin`'s public signals (and `getHashedCalldata`) to `chainId`/`verifyingContract`, consistent with `getSignedMessageHash`, to prevent cross-chain replay of the same calldata/proof pair.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as an allowed recipient/external action), and a mock ERC20 `VictimToken`.
2. Fund the `Emporium` contract directly with `VictimToken.transfer(emporium, 1000e18)` to simulate in-flight/protocol funds.
3. As an attacker EOA with no deposits, build `CircomData` with `dimensions.tokenNumber == 0`, `erc20TokenAddresses == []`, `externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalAddress == emporium`, and `externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: victimToken, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 1000e18))})], maxFee: 0, deadline: type(uint256).max})`.
4. Set `emporiumMessage = Poseidon(messageSeed)` for an attacker-chosen `messageSeed`, compute `calldataHash = getHashedCalldata(circomData)`, and generate a valid `MainEVMCircuitMin` proof locally with `snarkjs`.
5. Call `hinkal.transact(a, b, c, dimensions, circomData)`.
6. Assert: `VictimToken.balanceOf(emporium) == 0` before assertion of theft, `VictimToken.balanceOf(attacker) == 1000e18` after the call, and that no `require`/revert fired in either `EmporiumUpgradeable.runAction`'s balance loop or `Hinkal.transact`'s balance loop (both iterate zero-length `erc20TokenAddresses`), proving the equality "assets Emporium can move" != "assets accounted in balancesBefore/balancesAfter" is violated.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-118)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-317)
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

**File:** contracts/HinkalHelper.sol (L64-75)
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

**File:** contracts/Hinkal.sol (L78-97)
```text
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
```
