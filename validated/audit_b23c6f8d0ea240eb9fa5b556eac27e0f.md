### Title
Emporium `runAction` with a zero-token Min-circuit call executes arbitrary attacker-chosen calls with zero balance accounting, zero signature check, and zero UTXO spend, draining pooled ERC20/ETH balances — ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
When `circomData.erc20TokenAddresses.length == 0`, Hinkal routes the Emporium action to the `MainEVMCircuitMin` proof path, which proves nothing about `stack.ops`, nullifiers, or a Merkle root [1](#0-0) . All balance-conservation loops in `Hinkal.transact` and `EmporiumUpgradeable.runAction` iterate over `circomData.erc20TokenAddresses`, so with an empty array they execute zero iterations, and `EmporiumStack.signerAddress == address(0)` makes `verifyWallet` skip signature verification entirely, letting an unprivileged attacker submit arbitrary `EmporiumOperation`s that move Emporium's pooled token balances (deposited by other users) to themselves.

### Finding Description
**Broken equality:** Hinkal's design invariant is `balanceDif == amountChanges[i] + utxoAmount` for every token moved during a call (checked at [2](#0-1) ), and Emporium's mirrored invariant `balanceChange == -deltaAmountChanges[i] + (funds returned as UTXO)` (checked at [3](#0-2) ). Both loops range `for (i = 0; i < circomData.erc20TokenAddresses.length; i++)`. With `erc20TokenAddresses.length == 0`, this range is empty, so the equality is never evaluated for any token actually moved during the call — the two sides simply don't exist for this call.

**Root cause and path:**
1. `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin` (only `emporiumMessage`, `timeStamp`, `calldataHash` as public inputs) whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` [4](#0-3) .
2. `HinkalHelper.dimensionsCheck` only requires that array lengths equal `dimensions.tokenNumber`; it never forbids `tokenNumber == 0` for an external action [5](#0-4) .
3. `Hinkal.transact` verifies the (trivial) Min-circuit proof against a verifier keyed by `buildVerifierId(dimensions, externalActionId)` with `tokenNumber = 0` [6](#0-5) ; the Min circuit only constrains `message = Poseidon(messageSeed)`, `outTimeStamp`, `calldataHash` — no root, no nullifiers, no amounts [7](#0-6) .
4. `Hinkal._externalTransact` computes `deltaAmountChanges` over the empty `erc20TokenAddresses` array (0 elements) and calls `EmporiumUpgradeable.runAction` [8](#0-7) .
5. Inside `runAction`, `verifyWallet` is called; if the attacker sets `stack.signerAddress == address(0)`, it returns immediately after marking the message used — no ECDSA check at all [9](#0-8) .
6. The ops loop then treats every op as CASE 2 (since `signerAddress == address(0)` makes `op.invokeWallet && signerAddress != address(0)` false regardless of `invokeWallet`), and CASE 2 only blocks the two `IHinkalWallet` selectors — any other `endpoint`/`callData` is executed directly by the Emporium contract [10](#0-9) .
7. The post-loop balance/UTXO accounting loop (lines 132-151) iterates over `circomData.erc20TokenAddresses.length == 0`, i.e., zero times — nothing is checked or captured for whatever `ops` moved [11](#0-10) .
8. Back in `Hinkal.transact`, `oldBalances`/`newBalances` are also computed over the same empty `erc20TokenAddresses` array, so the outer balance-diff/slippage loop (lines 97-147) is likewise a no-op [12](#0-11) .

**Exact attacker call:** Craft an EOA transaction to `Hinkal.transact` with `dimensions.tokenNumber = 0`, `circomData.erc20TokenAddresses = []`, `circomData.externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `circomData.externalActionData.externalActionMetadata = abi.encode(EmporiumStack{signerAddress: address(0), ops: [EmporiumOperation{endpoint: <pooled_ERC20>, invokeWallet:false, value:0, callData: transfer(attacker, poolBalance)}], maxFee:0, deadline: far-future})`, and a self-generated `MainEVMCircuitMin` proof (only needs a self-chosen `messageSeed`; no UTXO secret knowledge required). This is fully reachable by an unprivileged attacker: no admin role, no other user's key, and no valid signature are needed because `signerAddress == address(0)` disables the EIP-712 check entirely.

Existing guards fail because: `performHinkalChecks`/`dimensionsCheck` never forbid `tokenNumber == 0` in combination with an external action that performs arbitrary calls; `verifyProof` succeeds because the Min circuit is a legitimately registered verifier for this dimension tuple and proves nothing about `ops`; `rootHashExists` is irrelevant since `rootHashHinkal` isn't even a Min-circuit signal; `insertNullifiers`/`insertCommitments` run on empty arrays; and Emporium's own balance-conservation loop and Hinkal's are both keyed to the same (empty) token array, so no check anywhere observes the funds leaving.

### Impact Explanation
Critical — direct theft of pooled ERC20 (or ETH, via `value`/native calls) that belongs to other Emporium depositors, with zero UTXOs spent and zero balance accounting. The attack is fully repeatable per token/message (bounded only by `usedMessages` per specific `emporiumMessage`, which the attacker freely chooses each time), and can be executed once per unique `emporiumMessage` to drain any and all ERC20/ETH balances the Emporium contract holds.

### Likelihood Explanation
High feasibility for an unprivileged attacker: only requires generating a trivial `MainEVMCircuitMin` proof (public inputs are attacker-chosen `emporiumMessage`/`timeStamp`/`calldataHash`, private input a self-chosen `messageSeed` — no secret knowledge of any real UTXO, nullifier, or Merkle path needed), constructing an `EmporiumStack` with `signerAddress = address(0)` to bypass signature checks, and having Emporium hold any positive pooled balance (true whenever any user has deposited into Emporium via the normal deposit flow). No special timing, races, or privileged roles are required.

### Recommendation
- Reject Min-circuit / `erc20TokenAddresses.length == 0` calls for the Emporium action whenever `stack.ops.length > 0` and there's no compensating balance/signature guarantee; alternatively, require that `stack.signerAddress != address(0)` (i.e., always require a valid EIP-712 signature over `ops`) whenever `erc20TokenAddresses.length == 0`.
- Bind `stack`/`ops` content into the circuit-proven `emporiumMessage`/`calldataHash` so a Min-circuit proof cannot authorize arbitrary `ops`, or forbid using the Min circuit whenever `externalActionData.externalActionMetadata` decodes to non-empty `ops`.
- In `EmporiumUpgradeable.runAction`, add an explicit balance-accounting mechanism independent of `circomData.erc20TokenAddresses` (e.g., verify no unaccounted token balances of the Emporium contract decreased across the whole `ops` execution, not just for tokens listed in the possibly-empty array).

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as registered external action), register the `mainEVMCircuitMin0v4` verifier for `buildVerifierId({tokenNumber:0,...}, HINKAL_EMPORIUM_ACTION_ID)`.
2. Have victim deposit `1000 USDC` into Hinkal with a normal transaction routed through Emporium (`deltaAmountChanges[i] > 0`), so Emporium's on-chain USDC balance is `1000`.
3. Generate a `MainEVMCircuitMin` proof off-chain via snarkjs with attacker-chosen `messageSeed`, `outTimeStamp`, `calldataHash`.
4. Build `circomData` with `erc20TokenAddresses=[]`, `amountChanges=[]`, `inputNullifiers=[]`, `outCommitments=[]`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionMetadata = abi.encode(EmporiumStack{signerAddress:address(0), ops:[{endpoint:USDC, invokeWallet:false, value:0, callData: abi.encodeCall(IERC20.transfer,(attacker, 1000e6))}], maxFee:0, deadline:type(uint256).max})`.
5. Call `Hinkal.transact(a,b,c,dimensions{tokenNumber:0,...}, circomData)` from attacker EOA.
6. Assert: call succeeds; `USDC.balanceOf(attacker)` increases by `1000e6`; `USDC.balanceOf(Emporium)` decreases by `1000e6`; assert both sides of the equality `balanceDif == amountChanges[i] + utxoAmount` were never evaluated (loop bound `circomData.erc20TokenAddresses.length == 0`), confirming zero balance-conservation checks were applied while real victim funds left the pool.

### Citations

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

**File:** contracts/Hinkal.sol (L36-65)
```text
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
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
            );
        }
```

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

**File:** contracts/Hinkal.sol (L244-260)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-157)
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

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
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
