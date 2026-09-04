This confirms the vulnerability. The `MainEVMCircuitMin` circuit's only computation is `message <== Poseidon(1)([messageSeed])` [1](#0-0)  — it proves nothing about UTXO ownership, nullifiers, roots, or amounts; `messageSeed` is a value the attacker freely chooses, so `emporiumMessage` is just an attacker-selected Poseidon output with no binding to any real deposit or balance.

### Title
Unauthenticated arbitrary call execution from Emporium via the Min-circuit path with `signerAddress == 0` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol, contracts/CircomDataBuilder.sol])

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, which only constrains `message`, `timeStamp`, and `calldataHash` [2](#0-1) . The underlying circuit `MainEVMCircuitMin` merely computes `Poseidon(messageSeed)` with no constraint tying it to any UTXO, nullifier, root, or amount [1](#0-0) . Combined with `EmporiumUpgradeable.verifyWallet` skipping signature verification entirely when `stack.signerAddress == address(0)` [3](#0-2) , any unprivileged caller can get `EmporiumUpgradeable.runAction` to execute arbitrary `op.endpoint.call{value: op.value}(op.callData)` from Emporium's identity [4](#0-3) , with the balance-accounting loop iterating zero tokens (since `erc20TokenAddresses` is empty) and therefore never detecting the change [5](#0-4) .

### Finding Description
**Broken equality:** assets Emporium can move/authorize in a transaction == assets accounted for in `balancesBefore`/`balancesAfter`. In this path the left side is unbounded (arbitrary `call` to any `endpoint`), while the right side is provably zero because `circomData.erc20TokenAddresses.length == 0` makes both balance arrays empty [6](#0-5) .

**Path:** Attacker calls `Hinkal.transact` with `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, and `externalActionMetadata` ABI-encoding an `EmporiumStack` where `signerAddress == address(0)` and `ops` contains e.g. `endpoint = <someERC20 held by Emporium>`, `callData = approve(attacker, type(uint256).max)` (or directly a `transfer`).

1. `hinkalHelper.performHinkalChecks` calls `CircomDataBuilder.formInputForCircom`, which detects the Emporium+empty-token condition and returns only 3 public signals via `formInputEmporiumMin` [2](#0-1) .
2. The attacker generates a trivial, always-satisfiable proof for `MainEVMCircuitMin` by picking any `messageSeed` and setting `emporiumMessage = Poseidon(messageSeed)` themselves — no relationship to real funds, roots, or nullifiers is enforced [1](#0-0) .
3. `Hinkal.transact` still requires `rootHashExists(circomData.rootHashHinkal, ...)` [7](#0-6) , but this only requires the root to be *some* existing historical root of the tree — it does not require the attacker to own any leaf under it, since no nullifier/ownership signal is part of the Min public input vector.
4. `_externalTransact` in `Hinkal.sol` iterates `erc20TokenAddresses` (empty) to build `deltaAmountChanges` (empty array) and calls `EmporiumUpgradeable.runAction` [8](#0-7) .
5. Inside `runAction`, `verifyWallet` is called; since `stack.signerAddress == address(0)`, it returns immediately after marking `usedMessages[emporiumMessage] = true`, performing **no signature check at all** [3](#0-2) .
6. The op loop then executes the attacker-supplied `op.endpoint.call{value: op.value}(op.callData)` unconditionally (Case 2, stateless interaction, since `stack.signerAddress == address(0)` disables the wallet-invocation branch) [9](#0-8) . This call executes with `msg.sender == EmporiumUpgradeable`, so any `approve()`/`transfer()` on a token where Emporium holds a balance succeeds using Emporium's own token balance/identity.
7. Because `erc20TokenAddresses.length == 0`, `balancesBefore`/`balancesAfter` are empty arrays, so the loop that would normally detect and revert on unauthorized balance changes (`BalanceChangeShouldBePositive`) never executes for the token being drained [10](#0-9) .
8. The attacker (or an accomplice in the same block/bundle) then calls `transferFrom` directly on the token contract using the granted allowance, moving Emporium's actual token balance to themselves — entirely outside Hinkal's accounting.

**Why guards fail:** `performHinkalChecks` validates `calldataHash` integrity, relay validity, `dimensionsCheck`, and `checkOnchainCreation`, but none of these constrain what `externalActionMetadata` (the `EmporiumStack`) contains, nor do they require `erc20TokenAddresses` to be non-empty for the Emporium action id. `verifyProof` only checks the trivial Poseidon relation. `rootHashExists` only checks root freshness, not ownership. `onlyAllowedRecipient` on `runAction` is satisfied because the call legitimately originates from `Hinkal` itself via `_externalTransact` — the vulnerability is that `Hinkal` unconditionally forwards attacker-controlled `EmporiumStack` data without any binding to real ownership when the Min-circuit/empty-token-array combination is chosen.

### Impact Explanation
Any unprivileged EOA can force `EmporiumUpgradeable` to execute an arbitrary external call (`approve`, `transfer`, or any other selector not equal to `callHinkalWallet`/`doSendToRelay`) from Emporium's own address, against any token/contract Emporium holds balance or privilege in, with zero accounting. This is direct theft of protocol/pooled funds held by the Emporium contract — funds belonging to other users who have deposited into Emporium — matching **Critical: direct theft of shielded or in-flight user funds**. The exploit is fully repeatable: each call only needs a fresh unused `emporiumMessage` value (trivial to generate), so the attacker can drain every token Emporium holds, one `approve`+`transferFrom` (or direct `transfer`) pair per token, across as many transactions/blocks as needed.

### Likelihood Explanation
Preconditions: Emporium must hold a non-zero token balance (true whenever any user has funds routed through Emporium). Attacker cost is minimal — generating the trivial `MainEVMCircuitMin` proof requires no special setup, and no signature or privileged role is needed since `signerAddress == address(0)` bypasses `verifyWallet`'s EIP-712 signature check entirely. This is fully feasible for any unprivileged caller and highly repeatable.

### Recommendation
- Require `erc20TokenAddresses.length > 0` for the Emporium action, or otherwise disallow the Min-circuit optimization from bypassing balance accounting when arbitrary `ops` with real external calls are present.
- Never allow `stack.signerAddress == address(0)` to bypass signature verification when `op.invokeWallet == false` and the op is a raw stateless call to an arbitrary `endpoint`/`callData`; the "self-service" mode (no wallet signature) should only be usable for internally-authorized, restricted operations (e.g., only calls into `msg.sender`'s own funds already accounted for via `deltaAmountChanges`) — not arbitrary calldata to arbitrary endpoints.
- Make the Min circuit path bind `message`/`calldataHash` to an actual proof of authorization over the `EmporiumStack.ops` hash, and/or require the accounting loop to run over the true set of tokens touched by `ops`, not just `circomData.erc20TokenAddresses`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as allowed recipient of Hinkal), and a mock ERC20 `TOKEN`.
2. Fund `Emporium` with `TOKEN.transfer(emporium, 1000e18)` to simulate pooled user deposits.
3. From an attacker EOA (no special role), construct `CircomData` with `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, `externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: address(TOKEN), invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.approve, (attacker, type(uint256).max))})], maxFee: 0, deadline: 0}))`.
4. Locally generate a valid Groth16 proof for `MainEVMCircuitMin` with a self-chosen `messageSeed`, setting `emporiumMessage = Poseidon(messageSeed)`, `timeStamp`, `calldataHash` matching `getHashedCalldata`.
5. Use an existing/root from `rootHashExists` (any historical root works, no ownership required).
6. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from the attacker.
7. Assert: `TOKEN.allowance(emporium, attacker) == type(uint256).max` after the call succeeds without revert.
8. In a follow-up call (same block), attacker calls `TOKEN.transferFrom(emporium, attacker, 1000e18)`.
9. Assert `TOKEN.balanceOf(attacker) == 1000e18` and `TOKEN.balanceOf(emporium) == 0`, proving direct theft of Emporium-held funds with zero balance-accounting revert throughout.

### Citations

**File:** circuits/MainEVMCircuitMin.circom (L6-17)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
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
