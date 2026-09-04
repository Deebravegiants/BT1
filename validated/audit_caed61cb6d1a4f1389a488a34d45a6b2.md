### Title
Emporium `runAction` with empty `erc20TokenAddresses` bypasses all balance/signature checks, allowing any unprivileged caller to sweep arbitrary ERC20/ETH balances resident on the Emporium contract via unconstrained op calls - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol], [File: contracts/CircomDataBuilder.sol])

### Summary
When `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, which only feeds `emporiumMessage`, `timeStamp`, and `calldataHash` into the "min" circuit `MainEVMCircuitMin`. That circuit proves nothing about fund ownership - it only checks `message == Poseidon(messageSeed)` for an attacker-chosen `messageSeed`. Combined with `EmporiumUpgradeable.runAction`'s signature bypass for `stack.signerAddress == address(0)` and its per-token balance accounting that is a no-op when `erc20TokenAddresses` is empty, any unprivileged EOA can force Emporium to execute arbitrary `op.endpoint.call{value: op.value}(op.callData)` calls with zero fund/authorization checks.

### Finding Description
Broken equality: `value entering Hinkal accounting (sum over amountChanges/utxoAmount for declared erc20TokenAddresses)` should equal `actual value moved/created by the executed ops`. When `erc20TokenAddresses.length == 0`, the left side is trivially `0` regardless of what the ops do.

Path:
1. `Hinkal.transact` calls `hinkalHelper.performHinkalChecks`, which calls `dimensionsCheck` [1](#0-0) . With `dimensions.tokenNumber == 0`, this forces `erc20TokenAddresses`, `amountChanges`, `inputNullifiers`, `outCommitments`, `onChainCreation`, `slippageValues` to all be empty - no root/nullifier constraint is ever placed on any token.
2. `performHinkalChecks` verifies `calldataHash` integrity via `getHashedCalldata(circomData) == circomData.calldataHash` [2](#0-1) , which is fully satisfiable by the attacker since it's a pure function of data they fully control.
3. `formInputForCircom` selects `formInputEmporiumMin` [3](#0-2) , whose only public inputs are `emporiumMessage`, `timeStamp`, `calldataHash`.
4. `MainEVMCircuitMin` constrains nothing about spend authority - `message <== Poseidon(1)([messageSeed])` with an attacker-chosen private `messageSeed` [4](#0-3) . Any attacker can trivially generate a valid proof.
5. `rootHashExists` in `Hinkal.transact` is checked against `circomData.rootHashHinkal`, but since no nullifiers/leaf is bound to this root in the min path, any historical root suffices without proving ownership of any leaf under it [5](#0-4) .
6. `_externalTransact` computes `deltaAmountChanges` over an empty array (no transfers into Emporium are required/tracked) and calls `IExternalActionV2(...).runAction` [6](#0-5) .
7. Inside `EmporiumUpgradeable.runAction`, `verifyWallet` returns immediately without any EIP-712 signature check when `stack.signerAddress == address(0)` [7](#0-6) . With `signerAddress == address(0)`, the condition `op.invokeWallet && stack.signerAddress != address(0)` is always false, so every op falls into the stateless branch, executing `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract with only a check that the selector isn't `callHinkalWallet`/`doSendToRelay` [8](#0-7) .
8. Balance accounting (`balancesBefore`/`balancesAfter`, `balanceChange < 0` revert, UTXO creation) is entirely computed over `circomData.erc20TokenAddresses`, which is empty, so the loop body never executes and no invariant is enforced on any token touched by the ops [9](#0-8) .

Exploit: attacker calls `Hinkal.transact` twice (or in sequence) with `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, `EmporiumStack.signerAddress = address(0)`, and an `op` whose `endpoint`/`callData` is an arbitrary call (e.g., a DEX swap landing output tokens on the Emporium contract, or directly `token.transfer(attacker, token.balanceOf(Emporium))`). Because neither call requires any signature, UTXO ownership proof, or per-token balance check, whatever ERC20/ETH balance is resident at the Emporium contract address (from any source - dust, fee remainders, or in-flight intermediate balances of other users' legitimate multi-op Emporium transactions) can be swept out to the attacker with no trace in `amountChanges`, `nullifiers`, or `utxoAmount`.

Why existing guards fail: `performHinkalChecks`'s `calldataHash` integrity check and `dimensionsCheck` only validate internal consistency of attacker-supplied data, not fund ownership; `rootHashExists` only checks the root is historically valid, not that the caller owns a leaf under it; the SNARK proof for the min circuit constrains nothing related to spend authority or the op contents.

### Impact Explanation
Any funds resident on the Emporium contract - whether protocol/relay fee remainders, dust, or in-flight balances from other users' legitimate multi-step Emporium operations - can be directly stolen by any unprivileged attacker with zero signature or accounting checks. This matches "Critical - direct theft of shielded or in-flight user funds" and also enables "executing calls... a wallet owner or prover never authorised" since arbitrary calls can be forced through Emporium's identity (e.g., to any token contract, any router) without any signer authorization. The exploit is fully repeatable per transaction and costs only gas plus a trivially generated proof.

### Likelihood Explanation
Preconditions are minimal: the attacker needs only to call `Hinkal.transact` with `externalActionId = HINKAL_EMPORIUM_ACTION_ID` and an all-zero `Dimensions`/empty `erc20TokenAddresses`, standard capabilities of any unprivileged EOA per the rules. Generating a valid proof for `MainEVMCircuitMin` requires no secret (attacker picks `messageSeed`). The only environmental requirement is that Emporium is registered as an external action (a normal, expected deployment state, not a privileged action by the attacker) and that some balance is resident on Emporium's address at the time of the sweep. This is straightforward to reproduce and repeatable indefinitely.

### Recommendation
Do not allow the "min" Emporium path (empty `erc20TokenAddresses`) to bypass wallet signature verification or fund-balance accounting. Specifically: (1) require `stack.signerAddress != address(0)` and a valid signature for any op that is not purely metadata/cancellation; (2) never allow the stateless branch (`op.endpoint.call`) to touch ERC20/ETH balances without those tokens being declared in `erc20TokenAddresses` and accounted for in `balancesBefore`/`balancesAfter`; (3) constrain the min circuit or an additional on-chain check to bind `calldataHash`/ops to a real spend-authorization proof, or disallow the min path from executing token-moving calls at all - restrict it strictly to zero-value, non-custodial operations (e.g., message cancellation).

### Proof of Concept
Foundry fork test plan:
1. Deploy `Hinkal`, `HinkalHelper`, register `EmporiumUpgradeable` as external action for `HINKAL_EMPORIUM_ACTION_ID`.
2. Send test ERC20 tokens directly to the Emporium contract address to simulate a resident/in-flight balance (`tokenOut.transfer(emporium, 1000e18)`).
3. As an unprivileged attacker EOA, build `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `externalActionData = {externalAddress: emporium, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: address(tokenOut), invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 1000e18))})], maxFee: 0, deadline: 0}))}`, and `calldataHash = getHashedCalldata(circomData)` computed off-chain.
4. Generate a snarkjs proof locally for `MainEVMCircuitMin` with an arbitrary `messageSeed`.
5. Call `Hinkal.transact` with this proof and data; assert it succeeds.
6. Assert `tokenOut.balanceOf(attacker)` increased by `1000e18` and `tokenOut.balanceOf(emporium)` decreased accordingly.
7. Assert no `Merkle` insertion (`tree`/`m_index`) occurred and no entry was added to `nullifiers`/`usedMessages` mapping for a real UTXO - i.e., left side (`amountChanges`/`utxoAmount` sum) stayed `0` while right side (actual token movement) was `1000e18`.

### Citations

**File:** contracts/HinkalHelper.sol (L64-91)
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

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
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

**File:** contracts/Hinkal.sol (L57-64)
```text
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-150)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L308-316)
```text
        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }
```
