### Title
Zero-`tokenNumber` Emporium call drains any resident ETH/ERC20 balance from `EmporiumUpgradeable` with no on-chain conservation check - ([File: contracts/Hinkal.sol:76-166, contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-160, contracts/CircomDataBuilder.sol:134-161, circuits/MainEVMCircuitMin.circom])

### Summary
When `dimensions.tokenNumber == 0` and `externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, which proves only `MainEVMCircuitMin` (a trivial `message = Poseidon(messageSeed)` circuit with no fund-related signals). Every balance-conservation loop in `Hinkal.transact` and `EmporiumUpgradeable.runAction` iterates over `circomData.erc20TokenAddresses` (length 0 in this mode), so none of them execute, while the attacker-controlled `EmporiumStack.ops` array (decoded from fully attacker-supplied `externalActionData.externalActionMetadata`) is iterated unconditionally and executes arbitrary `op.endpoint.call{value: op.value}(op.callData)`.

### Finding Description
The broken equality is: **tokens leaving an action == `-Σ deltaAmountChanges`**. With `tokenNumber = 0`, `deltaAmountChanges` is `new int256[](0)` (`contracts/Hinkal.sol` `_externalTransact`, `circomData.erc20TokenAddresses.length` used to size the array) [1](#0-0) , so the right-hand side is vacuously `0`, but the left-hand side is unconstrained.

Path:
1. `dimensionsCheck` only requires `erc20TokenAddresses.length == amountChanges.length == inputNullifiers.length == outCommitments.length == dimensions.tokenNumber`, so `tokenNumber = 0` is a legal, self-consistent input [2](#0-1) .
2. `formInputForCircom` detects this exact combination and swaps to `formInputEmporiumMin`, producing a public-input vector with only `emporiumMessage`, `timeStamp`, `calldataHash` [3](#0-2) ; `MainEVMCircuitMin` constrains nothing about balances/UTXOs [4](#0-3) .
3. In `Hinkal.transact`, `oldBalances`/`newBalances` are computed via `getBalancesForArray(circomData.erc20TokenAddresses)` (empty), and the reconciliation loop `for (uint64 i; i < circomData.erc20TokenAddresses.length; i++)` never runs [5](#0-4) .
4. `_externalTransact` calls `IExternalActionV2(externalAddress).runAction(circomData, deltaAmountChanges)` with an empty `deltaAmountChanges` array [6](#0-5) .
5. Inside `EmporiumUpgradeable.runAction`, `balancesBefore`/`balancesAfter` are likewise computed over the empty `erc20TokenAddresses` array, so the `BalanceChangeShouldBePositive` guard loop never executes [7](#0-6) . But the operations loop `for (uint256 i = 0; i < stack.ops.length; i++) { ... op.endpoint.call{value: op.value}(op.callData); }` is driven purely by `stack.ops.length`, which is independent of `tokenNumber`/`erc20TokenAddresses` and fully attacker-controlled via `abi.decode(circomData.externalActionData.externalActionMetadata, (EmporiumStack))` [8](#0-7) .
6. `verifyWallet` performs no signature check at all when `stack.signerAddress == address(0)` — it just marks `emporiumMessage` used and returns [9](#0-8) , so the attacker needs no valid EIP-712 signature to run arbitrary ops.
7. `payRelayFees` is also a no-op over the empty token array unless `feeStructure.flatFee != 0` and `signerAddress == address(0)` (in which case it reverts) — trivially avoided by setting `flatFee = 0` and `relay = address(0)`, which also sidesteps any relay-related requirement [10](#0-9) .

Root cause: the balance-conservation checks in both `Hinkal.transact` and `EmporiumUpgradeable.runAction` are keyed to `circomData.erc20TokenAddresses`/`deltaAmountChanges`, but the actual state-mutating operations (`stack.ops`) are keyed to an entirely separate, attacker-controlled array that has no size relationship to `tokenNumber`. Choosing `tokenNumber = 0` degrades the proof requirement to `MainEVMCircuitMin` and simultaneously empties every array the conservation checks depend on, while leaving the `ops` execution path fully live.

### Impact Explanation
An unprivileged EOA can drain any ETH or ERC20 balance resident in `EmporiumUpgradeable` (accumulated relay-fee dust, rounding remainders from `handleOut`, or stray/mistaken transfers) to an attacker-chosen recipient, with zero on-chain accounting tying the transferred value to any authorized amount. This is "executing calls or moving assets ... never authorised" and theft of protocol/relay-fee-adjacent resident funds — matching the **High** severity category (theft of protocol/relay fees / unauthorized asset movement). It does not reach shielded user UTXOs directly (those remain governed by the Merkle tree/nullifier logic, which is untouched here since `insertNullifiers`/`insertCommitments` are called with length-0 arrays), so it is bounded to whatever balance the Emporium contract happens to hold at attack time, but is fully repeatable every time such a balance reappears.

### Likelihood Explanation
Preconditions: (1) `EmporiumUpgradeable` must be registered as `HINKAL_EMPORIUM_ACTION_ID` in `Hinkal.externalActionMap` and listed as `_isAllowedRecipient` — both standard deployment conditions, not privileged actions by the attacker; (2) a verifier must be registered for `verifierId = keccak256(0,0,0,HINKAL_EMPORIUM_ACTION_ID)`, i.e., the `MainEVMCircuitMin` verifier, which this code path (`formInputEmporiumMin`) exists specifically to support, so it is presumed available in a functioning deployment; (3) `EmporiumUpgradeable` must hold a nonzero ETH/ERC20 balance (dust) at attack time. Attacker cost is a single `snarkjs` proof generation for a circuit with no meaningful constraints (`messageSeed` chosen freely) plus normal gas — trivially cheap and fully repeatable whenever dust reappears.

### Recommendation
Do not let `tokenNumber == 0` bypass balance accounting when `stack.ops.length > 0`. Either: (a) forbid the `MainEVMCircuitMin`/emporium-min proof path whenever `EmporiumOperation[]` is non-empty (require `tokenNumber >= 1` for any Emporium action with operations), or (b) make `EmporiumUpgradeable.runAction`'s before/after balance snapshot cover a token set derived independently from `stack.ops` (e.g., snapshot native ETH balance and any token addresses touched by `op.endpoint`/`op.callData`) rather than solely `circomData.erc20TokenAddresses`, and enforce `balanceChange == 0` (or `>= 0` with a matching UTXO output) unconditionally, not gated by the length of that array. Additionally, require a valid signature even when `signerAddress == address(0)` — or disallow zero-address signer entirely — so `ops` cannot be executed without cryptographic authorization from a genuine owner of the intended stealth funds.

### Proof of Concept
Foundry fork test plan:
1. Deploy/fork with real `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, and register a `MainEVMCircuitMin` verifier for `verifierId = buildVerifierId({tokenNumber:0, nullifierAmount:0, outputAmount:0}, HINKAL_EMPORIUM_ACTION_ID)`.
2. Seed `EmporiumUpgradeable` with dust: send 1 ETH directly (hits `receive()`) and transfer some ERC20 tokens to it directly (simulating relay-fee remainder).
3. Construct `EmporiumStack{ signerAddress: address(0), ops: [ { endpoint: attacker, invokeWallet: false, value: 1 ether, callData: "" }, { endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, dustAmount)) } ], maxFee: 0, deadline: type(uint256).max }`, ABI-encode into `externalActionMetadata`.
4. Build `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `inputNullifiers = []`, `outCommitments = []`, `dimensions.tokenNumber/nullifierAmount/outputAmount = 0`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `feeStructure.flatFee = 0`, `relay = address(0)`, `originalSender = attacker`.
5. Generate a `messageSeed`, compute `message = Poseidon(messageSeed)`, generate a genuine `MainEVMCircuitMin` snarkjs proof for the corresponding public inputs (`outTimeStamp`, `calldataHash`).
6. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from an unprivileged EOA.
7. Assert: `EmporiumUpgradeable`'s ETH balance decreases by 1 ether and attacker's ETH balance increases by 1 ether; ERC20 balance of Emporium decreases by `dustAmount`, attacker's ERC20 balance increases by `dustAmount`.
8. Assert `newBalances`/`oldBalances` arrays inside `Hinkal.transact` were length 0 (no revert from the reconciliation `require`s), confirming the conservation check never ran, i.e., `0 == 1 ether transferred` (broken equality) while the transaction succeeds.

### Citations

**File:** contracts/Hinkal.sol (L76-147)
```text
            UTXO[] memory utxoSet;

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
                int256 balanceDif;

                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
                );

                uint256 utxoAmount = 0;
                for (uint j = 0; j < utxoSet.length; j++) {
                    if (
                        utxoSet[j].erc20Address ==
                        circomData.erc20TokenAddresses[i]
                    ) {
                        utxoAmount += utxoSet[j].amount;

                        onChainCommitments[
                            onChainCommitmentCounter
                        ] = createOnchainCommitment(
                            utxoSet[j],
                            circomData.onChainEncryptedOutput
                        );
                        onChainCommitmentCounter++;
                    }
                }

                // balance equation to check: CHANGE IN BALANCE SHOULD EQUAL TO
                // 1) change in off-chain utxos
                // 2) change in on-chain utxos
                require(
                    balanceDif ==
                        (
                            circomData.onChainCreation[i]
                                ? int256(0)
                                : circomData.amountChanges[i]
                        ) +
                            int256(utxoAmount),
                    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
                );
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

**File:** contracts/HinkalHelper.sol (L64-109)
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

        uint previousNullifierAmount = circomData.inputNullifiers.length > 0
            ? circomData.inputNullifiers[0].length
            : 0;
        for (uint i = 1; i < circomData.inputNullifiers.length; i++) {
            require(
                circomData.inputNullifiers[i].length == previousNullifierAmount,
                "Nullifier amount should be equal"
            );
        }
        require(
            previousNullifierAmount == dimensions.nullifierAmount,
            "Actual and Claimed Nullifier Amount should be equal"
        );

        require(
            circomData.outCommitments.length == dimensions.tokenNumber,
            "OutCommitments number should be equal to token number"
        );
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

**File:** circuits/MainEVMCircuitMin.circom (L1-17)
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
