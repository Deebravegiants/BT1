### Title
Empty `erc20TokenAddresses` in the Emporium-min proof path bypasses all balance accounting in `EmporiumUpgradeable.runAction`, letting an unsigned (`signerAddress == 0`) `EmporiumStack` drain Emporium's/another action's balance for free - (File: `contracts/CircomDataBuilder.sol`, `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`formInputForCircom` routes any transaction with `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0` to `formInputEmporiumMin`, a "proof" that only constrains `message == Poseidon(messageSeed)` and a `calldataHash` binding — it constrains nothing about assets, nullifiers, or the Merkle root. Because `EmporiumUpgradeable.runAction` reuses this same (attacker-supplied, empty) `circomData.erc20TokenAddresses` array to bound its `balancesBefore`/`balancesAfter` accounting loop, an attacker who forces the min path gets the ops in their `EmporiumStack` executed with zero balance verification, and by setting `signerAddress == address(0)` they also skip the EIP-712 wallet-signature check in `verifyWallet`.

### Finding Description
The broken equality is: **assets Emporium can move in a tx == assets accounted in `balancesBefore`/`balancesAfter`**.

- `formInputForCircom` (contracts/CircomDataBuilder.sol:134-148) selects `formInputEmporiumMin` whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`. [1](#0-0) 
- `formInputEmporiumMin` only emits `emporiumMessage`, `timeStamp`, `calldataHash` as public signals — no token addresses, no `amountChanges`, no nullifiers, no root hash. [2](#0-1) 
- `performHinkalChecks` only verifies `getHashedCalldata(circomData) == circomData.calldataHash` (a self-consistency check the attacker trivially satisfies since they craft the whole `CircomData`), plus `dimensionsCheck`/`checkOnchainCreation`, none of which require `erc20TokenAddresses.length > 0`. [3](#0-2) 
- `EmporiumUpgradeable.runAction` decodes the attacker-controlled `EmporiumStack` from `externalActionMetadata`, then computes `balancesBefore`/`balancesAfter` strictly over `circomData.erc20TokenAddresses` — which is empty in the min path — so the accounting loop at lines 132-151 iterates zero times regardless of what the ops actually move. [4](#0-3) 
- `verifyWallet` skips the EIP-712 signature check entirely when `stack.signerAddress == address(0)`, only marking the message as used: [5](#0-4) 
- In the ops loop, when `signerAddress == 0`, `op.invokeWallet && stack.signerAddress != address(0)` is false, so every op falls into "CASE 2: Stateless Interaction" — an arbitrary `op.endpoint.call{value: op.value}(op.callData)` executed with `msg.sender == Emporium`. [6](#0-5) 

Exploit flow: the attacker calls `Hinkal.transact` with `externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, and a self-generated `emporiumMessage`/`messageSeed` (the min proof only proves knowledge of a seed the attacker itself picked — it says nothing about ownership of any funds). They set `externalActionMetadata` to an `EmporiumStack{ signerAddress: address(0), ops: [ { endpoint: <token or other allowed action address>, callData: <transfer/withdraw call>, value: ... } ] }`. Because `erc20TokenAddresses` is empty, `runAction`'s balance loop never runs, so whatever ERC20/ETH balance Emporium holds (deposits from other users' Emporium flows in-flight in the same block, or leftover balances) can be moved out via the op with no revert and no accounting/UTXO produced. If the target `endpoint` is another external action contract whose `onlyAllowedRecipient` modifier trusts calls where `msg.sender` is Emporium, the attacker can also pivot into that action's privileged logic from Emporium's identity.

None of the existing guards catch this: `performHinkalChecks`'s `calldataHash` check only proves self-consistency of attacker-supplied data, not fund ownership; `verifyProof`/circuit only proves `message == Poseidon(messageSeed)` in the min path; `onlyAllowedRecipient` on `EmporiumUpgradeable.runAction` only checks that `msg.sender == Hinkal`, not what the decoded ops do; `usedMessages` only prevents replay of the identical `emporiumMessage`, not repetition with fresh ones. This can be repeated per transaction/block with fresh `emporiumMessage` values, so it is repeatable across a batch.

### Impact Explanation
An unprivileged attacker can steal any ERC20/ETH balance sitting in the `EmporiumUpgradeable` contract (deposits from other users mid-flow, protocol fees routed through Emporium, or funds left temporarily on Emporium between operations) with a self-generated, unconstrained "proof," bypassing all wallet-signature and balance-accounting checks. This is direct theft of in-flight/shielded user funds and matches the Critical severity category.

### Likelihood Explanation
Preconditions are minimal and fully attacker-controlled: no privileged role is required, the attacker only needs (1) Emporium (or a trusted downstream action reachable via `onlyAllowedRecipient`) to hold a non-zero balance at call time, and (2) the ability to submit `Hinkal.transact` with `erc20TokenAddresses.length == 0` and a self-chosen `emporiumMessage`. Generating the min-circuit proof requires no real UTXO ownership, only knowledge of a self-chosen `messageSeed`. The attack is cheap (one transaction, gas only) and repeatable every block as long as Emporium holds funds, including racing other users' deposits landing in the same block.

### Recommendation
- Do not let `erc20TokenAddresses.length == 0` bypass balance accounting: `EmporiumUpgradeable.runAction` must independently enumerate/verify the tokens actually touched by the ops (e.g., require `erc20TokenAddresses` to cover every token/ETH balance affected, or snapshot Emporium's full balance sheet regardless of the proof path chosen).
- Do not allow the min-circuit path to authorize stateless arbitrary calls with `signerAddress == 0` unless the ops are separately, cryptographically bound to a specific, pre-approved operation set (not just a self-chosen `messageSeed`).
- Require `verifyWallet` to enforce signature verification (or an equivalent authorization) even when `signerAddress == 0`, rather than silently skipping to "return" after marking the message used.
- Ensure `formInputForCircom`'s selection of the min path cannot be attacker-triggered when the corresponding `EmporiumStack` performs external calls that move value out of Emporium.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as an allowed external action recipient), a mock ERC20, and fund `EmporiumUpgradeable` with `X` tokens (simulating in-flight/deposited balance).
2. As an attacker EOA (no special role), build `CircomData` with:
   - `externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID`
   - `erc20TokenAddresses = []`, `amountChanges = []`, `inputNullifiers = []`, `outCommitments = []`
   - `emporiumMessage = <attacker-chosen seed hash>`
   - `externalActionData.externalActionMetadata = abi.encode(EmporiumStack({ signerAddress: address(0), ops: [EmporiumOperation({ endpoint: address(mockERC20), invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, X)) })], maxFee: 0, deadline: 0 }))`
   - `calldataHash = getHashedCalldata(circomData)` (self-consistent, attacker-computed)
3. Generate the min-circuit proof locally proving only `message == Poseidon(messageSeed)` (no root/nullifier constraints needed).
4. Call `Hinkal.transact(proof, circomData, dimensions)`.
5. Assert **before**: `mockERC20.balanceOf(Emporium) == X`, `mockERC20.balanceOf(attacker) == 0`.
6. Assert **after**: `mockERC20.balanceOf(Emporium) == 0`, `mockERC20.balanceOf(attacker) == X`, with no revert from `BalanceChangeShouldBePositive` (the balance loop never ran because `circomData.erc20TokenAddresses.length == 0`).
7. Repeat step 2-6 in the same block with a new `emporiumMessage` to demonstrate repeatability across a batch.

### Citations

**File:** contracts/CircomDataBuilder.sol (L134-148)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-151)
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
