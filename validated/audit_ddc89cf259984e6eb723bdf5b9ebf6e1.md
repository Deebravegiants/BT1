### Title
`onlyAllowedRecipient` treats every allow-listed address equally, letting `EmporiumUpgradeable`'s stateless op relay a forged, proof-unchecked `CircomData` into `DepositOnChainUtxosExternalAction.runAction` - (File: `contracts/external-actions/DepositOnChainUtxosExternalAction.sol`)

### Summary
`ExternalActionBaseV2.onlyAllowedRecipient` (and its upgradeable twin) only checks `isAllowedRecipient[msg.sender]` and has no notion of "trusted, proof-checked caller" versus "another action forwarding an inner call." If `EmporiumUpgradeable` is registered in `DepositOnChainUtxosExternalAction`'s `isAllowedRecipient` map, its stateless-interaction branch (`op.endpoint.call{value: op.value}(op.callData)`) can target `DepositOnChainUtxosExternalAction.runAction` directly with a brand-new, attacker-crafted `CircomData` struct that never goes through `Hinkal._externalTransact` or `HinkalHelper.performHinkalChecks`.

### Finding Description
Broken equality claimed: `msg.sender == Hinkal (proof-checked path)` should be treated differently from `msg.sender == EmporiumUpgradeable (action-to-action forwarding)`, but `onlyAllowedRecipient` collapses both to the same boolean check: [1](#0-0) 

Reachable path: `Hinkal.transact` verifies the *outer* `circomData` via `hinkalHelper.performHinkalChecks` and `verifyProof`, then dispatches through `_externalTransact`, which checks `externalActionMap[externalActionId] == externalAddress` before calling `IExternalActionV2(externalAddress).runAction(...)`: [2](#0-1) 

If the outer action resolves to `EmporiumUpgradeable`, its `runAction` decodes `circomData.externalActionData.externalActionMetadata` into an `EmporiumStack` and, for each stateless op, performs a raw external call: [3](#0-2) 

The only filter on this call is a selector blacklist for `callHinkalWallet`/`doSendToRelay`; any other target and calldata is permitted. Critically, `verifyWallet` — the only authentication over `stack.ops` — is a no-op whenever `stack.signerAddress == address(0)`: [4](#0-3) 

so in stateless mode there is no signature binding the caller to a specific set of ops beyond what the attacker themselves supplied inside the outer `circomData` that they (as an unprivileged depositor) constructed and proved for their own transaction.

An attacker can therefore encode `op.callData = abi.encodeCall(DepositOnChainUtxosExternalAction.runAction, (forgedCircomData, zeroDeltas))` where `op.endpoint = address(DepositOnChainUtxosExternalAction)`. If that action's `isAllowedRecipient[EmporiumUpgradeable] == true` (precondition given), the resulting low-level call from inside `EmporiumUpgradeable.runAction` has `msg.sender == EmporiumUpgradeable`, which satisfies `onlyAllowedRecipient` even though this `forgedCircomData` was never submitted to `Hinkal.transact`, never hashed and compared in `HinkalHelper.performHinkalChecks` (`getHashedCalldata(circomData) == circomData.calldataHash`), and never fed as a Groth16 public input: [5](#0-4) 

Inside `DepositOnChainUtxosExternalAction.runAction`, every field of this forged struct — `originalSender`, `erc20TokenAddresses`, `externalActionMetadata` (the `utxoAmounts`) — is used directly to pull tokens: [6](#0-5) 

with `transferERC20TokenFrom` performing a plain `safeTransferFrom(_from, _to, _value)`: [7](#0-6) 

`_to` here resolves to `msg.sender` of the inner call, i.e. `EmporiumUpgradeable`'s address, so the attacker can set `originalSender` to any address that has previously granted an ERC20 allowance to the `EmporiumUpgradeable` contract, pulling those tokens with no proof, no nullifier check, and no root-hash validation for this inner action at all.

Existing guards do not prevent this: `performHinkalChecks`, `verifyProof`, `rootHashExists`, and `insertNullifiers` all operate exclusively on the *outer* `circomData` passed to `Hinkal.transact`; none of them ever see or constrain the *inner*, freshly-decoded `CircomData` struct built from raw `op.callData` bytes. `onlyAllowedRecipient` is address-only and cannot tell that this second `runAction` invocation is an unverified re-entry rather than the one sanctioned call from `Hinkal._externalTransact`.

### Impact Explanation
An attacker who is any unprivileged EOA can pull ERC20 tokens from arbitrary addresses that have an outstanding allowance to `EmporiumUpgradeable`, with zero nullifier/proof coverage on the pulled amount or victim address — this is a proof/nullifier-verification bypass enabling arbitrary token pulls, matching the Critical severity category (proof or nullifier verification bypass, direct theft of funds not authorized by the wallet owner). The attack is repeatable per victim/allowance and per transaction as long as allowance remains.

### Likelihood Explanation
This requires: (1) `DepositOnChainUtxosExternalAction` to have `isAllowedRecipient[EmporiumUpgradeable] == true` simultaneously with Hinkal — a deployment/admin configuration choice, not something the attacker controls, and I found no deployment script or test in the indexed codebase that confirms this dual-registration actually occurs in production; (2) a victim must have previously granted ERC20 allowance to the `EmporiumUpgradeable` contract address. Both are plausible operational states (Emporium is meant to hold/relay funds via allowances) but neither is guaranteed by the code alone — the vulnerability's exploitability is entirely gated by this admin-controlled allow-list configuration, which the attacker cannot set. Attacker cost is otherwise low: one self-generated valid proof for their own transaction plus crafting `op.callData`.

### Recommendation
Add an explicit guard distinguishing "true entrypoint" calls from Hinkal versus "forwarded" calls from other actions — e.g., require `msg.sender == hinkalAddress` for actions like `DepositOnChainUtxosExternalAction` that mint/pull funds based on unauthenticated `circomData.originalSender`, or forbid registering any action address (like Emporium) as an allowed recipient of another privileged-pull action. Alternatively, have `EmporiumUpgradeable`'s stateless branch disallow calling any address registered as a Hinkal external action (`externalActionMap` reverse lookup) to prevent action-to-action re-entry that bypasses `performHinkalChecks`.

### Proof of Concept
Hardhat test:
1. Deploy `Hinkal`, `HinkalHelper`, `DepositOnChainUtxosExternalAction` with `_allowedRecipients = [Hinkal, EmporiumUpgradeable]` (simulating the stipulated precondition), and `EmporiumUpgradeable`.
2. Have a "victim" account `approve(EmporiumUpgradeable, MAX)` on a test ERC20.
3. As attacker, build an `EmporiumStack` with `signerAddress = address(0)` and one stateless op: `endpoint = DepositOnChainUtxosExternalAction`, `callData = abi.encodeCall(runAction, (forgedCircomData, [0]))` where `forgedCircomData.originalSender = victim`, `erc20TokenAddresses = [testToken]`, `externalActionMetadata = abi.encode([[amount]])`, and `calldataHash` set to satisfy only the attacker's own outer proof (self-consistent, never checked against `forgedCircomData`).
4. Submit a valid Hinkal `transact` call (outer proof for the attacker's own UTXOs) whose `externalActionData.externalAddress = EmporiumUpgradeable`.
5. Assert: victim's token balance decreases by `amount` and `EmporiumUpgradeable`/attacker gains it, while asserting `CircomDataBuilder.getHashedCalldata(forgedCircomData) != forgedCircomData.calldataHash` (i.e., the inner struct was never validated) and that `forgedCircomData` was never part of any `Hinkal.transact` call's public inputs.

### Citations

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L16-22)
```text
    modifier onlyAllowedRecipient() {
        require(
            isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-113)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L314-316)
```text
        if (stack.signerAddress == address(0)) {
            return;
        }
```

**File:** contracts/HinkalHelper.sol (L208-225)
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
```

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
