### Title
Emporium Min-proof path lets any attacker execute unauthenticated, unaccounted `EmporiumOperation`s that drain Emporium's held balances - (File: `contracts/CircomDataBuilder.sol`, `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, a circuit that only proves knowledge of a self-chosen `messageSeed` and constrains nothing about tokens, amounts, or ops. Combined with `EmporiumStack.signerAddress == 0`, `verifyWallet` skips ECDSA signature verification entirely, so the attacker's arbitrary `ops` execute with no authorization anchor at all, as calls from Emporium's own address, while the balance accounting loop (scoped to the empty `erc20TokenAddresses` array) records nothing.

### Finding Description
The broken equality is: **assets Emporium can move in the transaction == assets accounted for in `balancesBefore`/`balancesAfter`**, and a second, compounding equality: **authorization for executing `EmporiumOperation`s == a valid ECDSA signature (when `signerAddress != 0`) OR a ZK proof that constrains the tokens/amounts moved**.

Path:
1. `Hinkal.transact` calls `hinkalHelper.performHinkalChecks`, which calls `CircomDataBuilder.formInputForCircom`: [1](#0-0) 
Because the attacker sets `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputEmporiumMin` is selected, whose only public/private inputs are `emporiumMessage`, `timeStamp`, `calldataHash` — no root hash, no nullifiers, no amounts, no token addresses are constrained by the proof: [2](#0-1) 
The circuit itself (`MainEVMCircuitMin`) simply proves `message == Poseidon(messageSeed)` for an attacker-chosen `messageSeed`, so anyone can generate a valid proof for any `emporiumMessage` they pick: [3](#0-2) 

2. `Hinkal.transact` proceeds to `_externalTransact`. Since `erc20TokenAddresses.length == 0`, `deltaAmountChanges` is an empty array, and the token-balance checks in `Hinkal.transact` (lines 78-90) are computed over an empty array too — i.e., no accounting whatsoever on the Hinkal side: [4](#0-3) [5](#0-4) 

3. `EmporiumUpgradeable.runAction` is called (passes `onlyAllowedRecipient` because `msg.sender == Hinkal`, which is legitimately allowed). It decodes the attacker-supplied `EmporiumStack` and computes `balancesBefore`/`balancesAfter` only over the (empty) `circomData.erc20TokenAddresses` array: [6](#0-5) 

4. `verifyWallet` is invoked. Since the attacker sets `stack.signerAddress == address(0)`, the function marks the message used and returns immediately — **no ECDSA signature verification occurs**: [7](#0-6) 

5. The `ops` loop then executes each attacker-controlled `EmporiumOperation`. With `stack.signerAddress == address(0)`, CASE 1 (invoking via `HinkalWallet`) is unreachable, so every op falls into CASE 2 and is executed as a raw low-level call **from the Emporium contract's own address**, with attacker-chosen `endpoint`, `callData`, and `value`: [8](#0-7) 

6. Because `circomData.erc20TokenAddresses` is empty (a precondition of reaching this cheap Min-proof path at all), `balancesBefore`/`balancesAfter` are zero-length, and the post-loop `for` loop that computes `balanceChange` and reverts with `BalanceChangeShouldBePositive` iterates zero times — it accounts for and validates nothing: [9](#0-8) 

Emporium is designed to legitimately hold token/ETH balances at its own address between operations — e.g. it has a bare `receive() external payable {}`, and `payRelayFees` explicitly transfers fee tokens directly from Emporium's own balance via `sendToRelay` when `signerAddress == address(0)`: [10](#0-9) [11](#0-10) 
Any such balance (fees, dust, in-flight funds) is now callable/spendable by an attacker's arbitrary `op.endpoint.call{value: op.value}(op.callData)`, e.g. `ERC20.transfer(attacker, amount)` where `msg.sender` inside that call is Emporium, directly stealing whatever ERC20/ETH Emporium is holding.

**Why existing guards fail:** `onlyAllowedRecipient` only checks that the caller of `runAction` is `Hinkal` (always true) — it says nothing about what the decoded `ops` are allowed to do. `verifyWallet`'s signature check is bypassable simply by setting `signerAddress == address(0)`. The ZK proof for this specific `(HINKAL_EMPORIUM_ACTION_ID, erc20TokenAddresses.length==0)` combination constrains nothing about tokens/amounts/ops (`formInputEmporiumMin`). `rootHashExists` is satisfied trivially since `rootHashHinkal` is not even a Min-circuit public input, so any historical (public) root works. `dimensionsCheck`/`checkOnchainCreation` only validate array-length consistency, not authorization of `ops`.

Note: `prooflessDeposit` itself is a separate, unrelated entrypoint (it never touches `externalActionData`/Emporium/`transact`); the exploit does not require it and doesn't depend on it — the vulnerable path is fully reachable purely through `Hinkal.transact` with a self-forged Min proof.

### Impact Explanation
An unprivileged attacker can direct the Emporium contract to execute arbitrary external calls under Emporium's own identity, with zero economic constraint from the ZK proof and zero authorization from a signature, while the accounting loop that is supposed to bound "what Emporium can end up owing/losing" is empty by construction. Any ERC20 or ETH balance sitting in the Emporium contract (relay fees paid out of Emporium's own balance, dust, or funds in flight from other users' partially executed EmporiumStacks) can be transferred to the attacker. This is direct theft of protocol/relay funds or in-flight user funds held by Emporium — Critical severity.

### Likelihood Explanation
No special preconditions beyond Emporium holding any nonzero balance at call time (which the protocol's own fee-payment design guarantees will happen: `payRelayFees` moves fee tokens through Emporium's own balance). The attacker needs only to: generate a trivial Min-circuit proof for a self-chosen `messageSeed`/`emporiumMessage`, pick any valid historical root hash, set `erc20TokenAddresses = []`, and craft an `EmporiumStack` with `signerAddress = address(0)` and malicious `ops`. No relay, admin, or victim cooperation is required, and the attack is repeatable for every non-zero balance Emporium accumulates.

### Recommendation
Do not allow `EmporiumUpgradeable.runAction` to execute stateless (CASE 2) `ops` when `stack.signerAddress == address(0)` unless the transaction's own ZK proof independently constrains every token/amount touched (i.e., disallow the Min-proof + empty-token-list combination from being paired with arbitrary unsigned `ops`, or require `erc20TokenAddresses`/`deltaAmountChanges` to enumerate every asset an op can touch and enforce the balance-delta check against that same set). At minimum, require a valid signature (or an equally strong authorization) whenever `ops.length > 0`, regardless of `signerAddress == 0`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (registered as the `HINKAL_EMPORIUM_ACTION_ID` external action and allowed recipient), and the `VerifierEVMMin0v4`/`mainEVMCircuitMin0v4` verifier.
2. Fund Emporium directly with, e.g., 10 WETH (simulating leftover relay-fee balance from `payRelayFees`), and record `balanceBefore = WETH.balanceOf(emporium)`.
3. Off-chain, generate a real Min-circuit proof for an attacker-chosen `messageSeed`, deriving `emporiumMessage = Poseidon(messageSeed)`.
4. Build `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, matching empty arrays for `inputNullifiers`/`outCommitments`/`onChainCreation`/`slippageValues`, `externalActionData = {externalAddress: emporium, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: WETH, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 10e18))})], maxFee: 0, deadline: type(uint256).max, v:0, r:0, s:0}))}`, and `rootHashHinkal` set to a known valid root, `rootHashHinkalIndex` pointing to it.
5. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from the attacker EOA.
6. Assert: `WETH.balanceOf(attacker) == 10e18` and `WETH.balanceOf(emporium) == balanceBefore - 10e18`, demonstrating theft of Emporium's held balance with no accounting (`balancesBefore`/`balancesAfter` arrays were length 0) and no signature check performed (`verifyWallet` returned early on `signerAddress == address(0)`).

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

**File:** contracts/Hinkal.sol (L76-90)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-90)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L226-245)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L369-369)
```text
    receive() external payable {}
```
