### Title
Unbounded `externalActionMetadata` + standing `approveUnlimited` allowance lets an attacker drain any residual/stranded token balance from `LifiExternalAction` as their own swap output - (`contracts/external-actions/swaps/LifiExternalAction.sol` / `contracts/external-actions/swaps/ExternalActionSwap.sol`)

### Summary
`ExternalActionSwap.swap` computes `inputAmount = uint256(-deltaAmounts[0])` (the amount Hinkal just transferred to the action for this call) but never enforces that this value bounds what the router is allowed to pull. `LifiExternalAction.callRouter` grants the router an unlimited ERC-20 approval via `approveUnlimited` and then executes fully attacker-supplied `externalActionMetadata`, which alone determines how much of the action's ERC-20 balance the router consumes. If the action contract ever holds a residual/stray balance of the input token (dust, a stuck prior swap, an accidental direct transfer, etc.), an attacker can craft `externalActionMetadata` for their own (perfectly valid, non-reused) proof that instructs the router to pull the deposited amount *plus* the residual balance, and the extra output is captured entirely as their own UTXO.

### Finding Description
The claimed invariant is: *tokens leaving the action in a tx == `-deltaAmountChanges` Hinkal sent it that tx*.

Trace:
- `Hinkal._externalTransact` (`contracts/Hinkal.sol:244-256`) transfers exactly `uint256(-deltaAmountChanges[i])` to the action address for negative deltas, then calls `IExternalActionV2.runAction`.
- `ExternalActionSwap.swap` (`contracts/external-actions/swaps/ExternalActionSwap.sol:40-68`) computes `inputAmount = uint256(-deltaAmounts[0])` and passes it into `callRouter`, but this value is **only used for the native-ETH branch** (`router.call{value: inputAmount}(...)`).
- `LifiExternalAction.callRouter` (`contracts/external-actions/swaps/LifiExternalAction.sol:16-36`), for the ERC-20 branch, does:
  ```solidity
  approveUnlimited(inputToken, router);
  (bool success, ) = router.call(externalActionMetadata);
  ```
  `inputAmount` is **never passed to the router call or used to cap the transfer**. The only thing that determines how much `inputToken` the router pulls from the action's balance is the router-encoded amount inside `externalActionMetadata`, which is fully attacker-controlled (it's part of `circomData.externalActionData` submitted by the caller).
- `swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore` after the router call is then, minus fees, sent wholesale to `msg.sender` (Hinkal) and packaged into `utxoSet[0]` bound to the attacker's own `circomData.stealthAddressStructure` (`ExternalActionSwap.sol:91-101`).
- Back in `Hinkal.transact` (`contracts/Hinkal.sol:97-146`), the final check only verifies internal self-consistency: `balanceDif == amountChanges[i] + utxoAmount`. Since the action genuinely transferred the larger `swappedAmount` to Hinkal, and the UTXO the action returns is exactly `swappedAmount - fees`, this check passes — it has no way to know that part of the input consumed by the router came from a pre-existing/stranded balance rather than from `-deltaAmountChanges[0]` of this transaction.
- `performHinkalChecks`/`CircomDataBuilder.getHashedCalldata` (`contracts/HinkalHelper.sol:221-225`, `contracts/CircomDataBuilder.sol:10-35`) and the SNARK public-input binding (`calldataHash` is a public input, `contracts/CircomDataBuilder.sol:160,234`) do cryptographically bind the proof to the *exact* `externalActionMetadata` bytes submitted — so the "same proof reused with mutated calldata" framing from the question does not work; a Groth16 proof cannot be reused against a different public-input vector. **However**, this binding does not need to be broken for the exploit: the attacker simply crafts fresh, self-consistent `externalActionMetadata` for their own (small) legitimate deposit, and generates their own valid proof for it. The bug is not proof/calldata forgery — it is that `inputAmount` (derived from `-deltaAmounts[0]`, which the proof does constrain) is never actually enforced as a ceiling on what the router may pull, because of the combination of `approveUnlimited` (no per-call allowance cap) and letting the router calldata (not the protocol) decide the pulled amount.

Attacker's call: submit `Hinkal.transact` with a tiny genuine deposit of `inputToken` (e.g. 1 wei) routed through `LifiExternalAction`, but with `externalActionMetadata` encoding a LI.FI router swap that pulls the action contract's *entire* `inputToken` balance (deposit + any residual sitting in the action from prior stuck/partial transactions or stray transfers). The router swaps that full balance to `outputToken`; the entire proceeds (minus the tiny relay/hinkal fee) are sent back to Hinkal and minted as the attacker's own private UTXO.

### Impact Explanation
Any ERC-20 (or native, though the ETH branch is amount-limited by `msg.value`) balance that becomes stranded in `LifiExternalAction` — from dust left after a partial/failed swap, a mis-sized approval consumption, or an accidental/direct token transfer to the action address — can be swept entirely by any unprivileged attacker into their own shielded output on their next self-initiated swap transaction, with no relation to what they actually deposited. This is direct theft of funds parked in the action that were never counted in that attacker's `-deltaAmountChanges`, matching **Critical: direct theft of shielded or in-flight user funds**. It is repeatable each time residual balance accumulates in the action contract.

### Likelihood Explanation
Preconditions: a non-zero residual `inputToken` balance must exist in `LifiExternalAction` at the time of the attack. This can arise from any prior partial LI.FI route execution (common with aggregator "path" swaps that don't always fully consume the approved/transferred amount), rounding/dust, or a stray direct ERC-20 transfer to the action's address (which anyone, including the attacker themselves in a prior step, could create at negligible cost). Given `approveUnlimited` leaves a permanent unlimited allowance and `callRouter` places no cap tied to `inputAmount`, exploitation cost is only gas plus generating one valid proof for a minimal deposit — well within reach of any unprivileged EOA. The attacker fully controls `externalActionMetadata`, so the only variable outside their control is whether/how much residual balance currently sits in the action contract, which they can also actively create over multiple transactions if router execution consistently leaves small dust behind.

### Recommendation
Enforce `inputAmount` as a hard cap on the ERC-20 pulled by the router in `LifiExternalAction.callRouter`: approve the router for exactly `inputAmount` (not `type(uint256).max`) immediately before the call and reset/verify the allowance afterward, and/or explicitly check that `balanceBefore(inputToken) - balanceAfter(inputToken) <= inputAmount` after the router call, reverting otherwise. More generally, `ExternalActionSwap`/`LifiExternalAction` should never hold or expose more balance to the router than what was transferred in for the current call — track and validate per-call input consumption rather than relying on ambient contract balance and unlimited allowances.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `LifiExternalAction` (with a mock LI.FI router), and register the action.
2. Seed the residual: directly `transfer` e.g. 100 `inputToken` to the `LifiExternalAction` contract address (simulating stranded dust/leftover from a prior partial swap), outside of any Hinkal transaction.
3. Attacker deposits 1 `inputToken` via a legitimate small UTXO and constructs a valid proof + `CircomData` with `amountChanges[0] = -1` (only 1 unit committed), `erc20TokenAddresses = [inputToken, outputToken]`.
4. Craft `externalActionMetadata` calling the mock router's swap function with `amountIn = 101` (1 deposited + 100 residual) sourced via `transferFrom(action, router, 101)` using the standing unlimited allowance.
5. Call `Hinkal.transact` with this data.
6. Assert: `swappedAmount` (and thus `utxoAmount`/attacker's minted UTXO) corresponds to swapping 101 `inputToken`, not 1; assert `LifiExternalAction`'s residual `inputToken` balance goes from 100 to 0 even though the attacker's `-deltaAmountChanges[0]` was only 1; assert the attacker's private balance/UTXO gained value equal to the 100-unit residual swap output, which was never part of their `-deltaAmountChanges` for that transaction — breaking the target equality. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L40-68)
```text
    function swap(
        CircomData calldata circomData,
        int256[] calldata deltaAmounts
    ) internal returns (UTXO[] memory utxoSet) {
        address inputToken = circomData.erc20TokenAddresses[0];
        uint256 inputAmount = uint256(-deltaAmounts[0]);

        if (inputToken == circomData.feeStructure.feeToken) {
            inputAmount -= circomData.feeStructure.flatFee;
        }

        address outputToken = circomData.erc20TokenAddresses[1];

        require(
            circomData.slippageValues[1] != 0,
            "swap output slippage floor not set"
        );

        require(
            block.timestamp <= circomData.timeStamp + SWAP_DEADLINE_WINDOW,
            "swap expired"
        );

        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );
```

**File:** contracts/external-actions/swaps/LifiExternalAction.sol (L16-36)
```text
    function callRouter(
        address inputToken,
        uint256 inputAmount,
        address outputToken,
        bytes calldata externalActionMetadata
    ) internal override returns (uint256 swappedAmount) {
        uint256 balanceBefore = getERC20OrETHBalance(outputToken);

        if (inputToken == address(0)) {
            (bool success, ) = router.call{value: inputAmount}(
                externalActionMetadata
            );
            require(success, "LI.FI swap failed: native coin");
        } else {
            approveUnlimited(inputToken, router);
            (bool success, ) = router.call(externalActionMetadata);
            require(success, "LI.FI swap failed: erc-20 token");
        }

        swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore;
    }
```

**File:** contracts/Hinkal.sol (L97-146)
```text
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

**File:** contracts/CircomDataBuilder.sol (L180-240)
```text
    function formBasicInput(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256[] memory input,
        uint256 index,
        uint256 emporiumMessage
    ) internal pure returns (uint256[] memory) {
        // 1) First we list public inputs as in the body of the main template (not the one with exact dimensions)
        input[index++] = circomData.stealthAddressStructure.H1x;
        input[index++] = circomData.stealthAddressStructure.H1y;
        input[index++] = circomData.stealthAddressStructure.stealthAddress;
        input[index++] = emporiumMessage; // this is for Emporium message signature verification

        // 2) Then we list the private inputs as in the body of the main template
        input[index++] = circomData.rootHashHinkal;
        input[index++] = getSignedMessageHash(
            chainId,
            verifyingContract,
            circomData,
            emporiumMessage
        );

        for (uint16 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            input[index++] = uint256(
                uint160(circomData.erc20TokenAddresses[i])
            );
        }

        for (uint16 i = 0; i < circomData.amountChanges.length; i++) {
            require(
                circomData.amountChanges[i] < MAX_AMOUNT &&
                    circomData.amountChanges[i] > -1 * MAX_AMOUNT,
                "amount changed is too large"
            );

            input[index++] = circomData.amountChanges[i] >= 0
                ? uint256(circomData.amountChanges[i])
                : CIRCOM_P - uint256(-circomData.amountChanges[i]);
        }

        for (uint16 i = 0; i < circomData.inputNullifiers.length; i++) {
            for (uint16 j = 0; j < circomData.inputNullifiers[i].length; j++) {
                input[index++] = circomData.inputNullifiers[i][j];
            }
        }

        input[index++] = circomData.timeStamp;

        for (uint16 i = 0; i < circomData.outCommitments.length; i++) {
            for (uint16 j = 0; j < circomData.outCommitments[i].length; j++) {
                input[index++] = circomData.outCommitments[i][j];
            }
        }
        input[index++] = circomData.calldataHash;

        input[index++] = circomData.stealthAddressStructure.H0x;
        input[index++] = circomData.stealthAddressStructure.H0y;

        return input;
    }
```
