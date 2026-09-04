### Title
Emporium ETH accounting bypass allows theft of contract's native ETH balance via unlisted `address(0)` in `erc20TokenAddresses` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` only tracks balance changes for tokens present in `circomData.erc20TokenAddresses`, but `EmporiumOperation.value` (native ETH sent via `op.endpoint.call{value: op.value}(...)` in CASE 2) is completely independent of that array. An attacker can craft a self-generated proof/transaction whose `erc20TokenAddresses` omits `address(0)` while still including an `EmporiumOperation` with a non-zero `value` pointing at an attacker-controlled endpoint, draining any ETH sitting in the Emporium contract's balance with zero on-chain accounting or reversion.

### Finding Description
The broken equality is: *total ETH leaving the Emporium contract via `op.value` calls should be reflected in, and bounded by, `circomData.amountChanges`/`deltaAmountChanges` for `address(0)`*. In practice, `runAction` only snapshots and diff-checks balances for indices present in `circomData.erc20TokenAddresses`: [1](#0-0) [2](#0-1) 

Meanwhile, CASE 2 spends ETH directly from the Emporium contract's own balance based solely on the attacker-chosen `EmporiumOperation.value` and `endpoint`, with no relation to `erc20TokenAddresses`: [3](#0-2) 

Nothing in the circuit or on-chain checks forces `address(0)` to be included in `erc20TokenAddresses` whenever an op has `value > 0`. The circuit only hashes `externalActionData` (which contains the abi-encoded `EmporiumStack`/ops) into `calldataHash`/`signedMessageHash` for integrity, it never inspects or constrains the ops' `endpoint`/`value` fields against `erc20TokenAddresses` or `amountChanges`: [4](#0-3) [5](#0-4) 

Since `runAction` is only reachable through the trusted `Hinkal.transact` path (`onlyAllowedRecipient` restricts `msg.sender` to the whitelisted Hinkal contract), the attacker cannot call it directly — but they fully control every field of their own proof and `CircomData`, including `erc20TokenAddresses` (their choice of which tokens to list) and the entire `EmporiumStack` metadata (since it is merely hashed, not semantically checked, by the circuit): [6](#0-5) 

Exploit flow:
1. Attacker deposits/owns a legitimate UTXO for some unrelated token (e.g., tokenA), sufficient to build a valid proof with `erc20TokenAddresses = [tokenA]`, `amountChanges[0] = 0` (no real deposit/withdraw needed).
2. Attacker crafts `externalActionMetadata` as an `EmporiumStack` with `signerAddress = address(0)` (skips wallet-signature verification per `verifyWallet`) and one `EmporiumOperation{ endpoint: attackerAddress, invokeWallet: false, value: <Emporium's current ETH balance>, callData: "" }`.
3. Attacker calls `Hinkal.transact` with this proof/circomData. `_externalTransact` computes `deltaAmountChanges` only for `tokenA` (zero), so no ETH is pre-funded into Emporium, and none is required to be.
4. Inside `runAction`, `balancesBefore`/`balancesAfter` are computed only over `[tokenA]`. CASE 2 executes `attackerAddress.call{value: op.value}("")`, draining the Emporium's full ETH balance to the attacker.
5. The check loop (lines 132-151) never touches index for `address(0)` because it isn't in `erc20TokenAddresses`, so `BalanceChangeShouldBePositive` and the slippage/balance-diff equality in `Hinkal.transact` (lines 97-146) never see this drain and cannot revert it.

Existing guards fail because: `performHinkalChecks`, `verifyProof`, and `rootHashExists` validate the attacker's own nullifiers/commitments/UTXO state (which are legitimately theirs), not the semantic content of `externalActionMetadata` against `erc20TokenAddresses`; `dimensionsCheck` only bounds array lengths declared by the attacker, not their content; and `BalanceChangeShouldBePositive`/slippage checks are scoped strictly to the attacker-chosen `erc20TokenAddresses` array, which the attacker deliberately leaves ETH out of.

### Impact Explanation
Any ETH held by the Emporium contract (from the `receive() external payable {}` fallback, refunds from op endpoints that return excess ETH, dust left by other users' Emporium transactions that also excluded `address(0)`, or other misdirected transfers) can be drained by an unprivileged attacker to an address of their choosing, with zero accounting, zero revert conditions, and no relation to their own shielded balance. This is direct theft of funds held by the contract (which may belong to other users or the protocol), matching the Critical category ("direct theft of shielded or in-flight user funds"). It is repeatable every time the Emporium accrues an ETH balance.

### Likelihood Explanation
Preconditions: (1) the Emporium contract must hold some non-zero ETH balance (achievable via its unrestricted `receive()` function, or via routine refunds from external DEX/router endpoints invoked by other Emporium operations); (2) attacker needs one legitimate self-owned UTXO to generate a syntactically valid proof (trivial, low cost — they can even use `amountChanges = 0` for an unrelated token). No relay, admin, or signer cooperation is required (`signerAddress = address(0)` bypasses `verifyWallet`'s signature checks). This is fully attacker-controlled and repeatable each time ETH balance accrues in the contract.

### Recommendation
Enforce that `address(0)` must be present in `circomData.erc20TokenAddresses` (with a corresponding tracked balance snapshot/diff) whenever any `EmporiumOperation.value > 0` is used in CASE 2 or CASE 1. Alternatively, track a separate `ethBalanceBefore`/`ethBalanceAfter` unconditionally in `runAction` regardless of whether `address(0)` is listed, and apply the same `BalanceChangeShouldBePositive` and balance-diff constraints to it, reverting if unaccounted ETH leaves the contract.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, and a mock ERC20 (`tokenA`); register Emporium as an external action and allowed recipient.
2. Send ETH directly to the Emporium contract via its `receive()` (simulating dust/refund accumulation), e.g. `vm.deal` + low-level `call{value: 5 ether}("")`.
3. As the attacker, deposit `tokenA` into Hinkal to obtain one real UTXO.
4. Off-chain, generate a valid Groth16 proof for a `transact` call with `erc20TokenAddresses = [tokenA]`, `amountChanges = [0]`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, and `externalActionMetadata` = abi-encoded `EmporiumStack{ signerAddress: address(0), ops: [EmporiumOperation{endpoint: attackerEOA, invokeWallet: false, value: 5 ether, callData: ""}] }`.
5. Call `Hinkal.transact(...)` with this proof.
6. Assert: `attackerEOA.balance` increases by `5 ether`; `address(emporium).balance` decreases by `5 ether`; the `transact` call does NOT revert (`BalanceChangeShouldBePositive` and the `balanceDif == amountChanges + utxoAmount` check in `Hinkal.sol` both pass because index for `address(0)` was never iterated).
7. Compare both sides of the equality explicitly: before, `emporium.balance = 5 ether`, `sum(deltaAmountChanges for address(0)) = undefined/never checked`; after, `emporium.balance = 0`, yet no on-chain invariant recorded or rejected the 5 ether outflow.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-151)
```text
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

**File:** contracts/CircomDataBuilder.sol (L20-35)
```text
    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
            );
    }
```

**File:** circuits/MainEVMCircuit.circom (L164-169)
```text
      outTotal += outAmounts[i][j];
    }

      // for each token type, the sum of refund and swapped amount should be equal to the sum of input amounts
      inTotal + amountChanges[i] === outTotal;
	}
```

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L39-46)
```text
    modifier onlyAllowedRecipient() {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();
        require(
            $._isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```
