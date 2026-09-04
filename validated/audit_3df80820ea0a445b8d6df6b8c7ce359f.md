### Title
Unaccounted ETH drain from `EmporiumUpgradeable` via empty-`erc20TokenAddresses` (min-circuit) `runAction` calls - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol::runAction)

### Summary
When `circomData.erc20TokenAddresses` is empty (the "min-circuit" Emporium path, gated by `CircomDataBuilder.formInputEmporiumMin`), `EmporiumUpgradeable.runAction` still executes `op.endpoint.call{value: op.value}(op.callData)` for every operation in the attacker-supplied `EmporiumStack`, but the balance-accounting loops (`balancesBefore`/`balancesAfter`) iterate zero times, so no equality is ever checked against the ETH that leaves the contract. Combined with `verifyWallet` short-circuiting (no signature check) when `stack.signerAddress == address(0)`, any unprivileged caller can craft a min-circuit Emporium op with `op.endpoint = attacker`, `invokeWallet = false`, and `op.value` up to Emporium's actual ETH balance, draining any ETH sitting on the `EmporiumUpgradeable` contract with zero accounting and zero authorization.

### Finding Description
The claimed broken equality: "ETH moved by `op.endpoint.call{value: X}` == 0 (the balancesBefore/After ETH accounting, which is skipped since `address(0)` isn't in the empty `erc20TokenAddresses` array)."

Tracing `runAction`: [1](#0-0) 

- `balancesBefore`/`balancesAfter` are computed via `getBalancesForArray(circomData.erc20TokenAddresses)`, which loops over the token list; with `erc20TokenAddresses.length == 0` this is a no-op loop.
- The `for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++)` block that computes `balanceChange` and reverts on `balanceChange < 0` (line 132-144) never runs, so no equality between what left/entered Emporium and `deltaAmountChanges` is ever enforced for this call.
- Meanwhile the ops loop (lines 91-118) unconditionally performs `op.endpoint.call{value: op.value}(op.callData)` for CASE 2 (`invokeWallet` false, or `signerAddress == address(0)`), spending Emporium's own ETH balance (since `address(this)` is the caller of `.call`).
- `verifyWallet` [2](#0-1)  only marks `usedMessages[emporiumMessage] = true` and returns immediately when `stack.signerAddress == address(0)` — no EIP-712 signature is required in that branch.
- `dimensionsCheck` in `HinkalHelper` requires `amountChanges.length == tokenNumber` and `erc20TokenAddresses.length == tokenNumber`, so choosing `tokenNumber = 0` legitimately produces the min-circuit path with `deltaAmountChanges` also being a zero-length array (`Hinkal.sol::_externalTransact` builds `deltaAmountChanges` sized to `erc20TokenAddresses.length`), so there is no ownership/nullifier constraint tying `op.value` to any UTXO the attacker actually owns.

Attacker's exact call: submit `Hinkal.transact` with a valid proof for `dimensions.tokenNumber = 0` (min-circuit, requires only `formInputEmporiumMin`'s three public signals: `emporiumMessage`, `timeStamp`, `calldataHash`, all attacker-chosen and self-consistent), `externalActionData.externalActionId` = Emporium's registered id, and `externalActionData.externalActionMetadata = abi.encode(EmporiumStack({ops: [EmporiumOperation({endpoint: attacker, invokeWallet: false, value: X, callData: ""})], signerAddress: address(0), maxFee: 0, deadline: <future>, v/r/s: unused}))`. `runAction` executes `attacker.call{value: X}("")`, transferring `X` wei straight out of Emporium's balance with no check that it corresponds to anything the attacker deposited.

Why existing guards fail: `onlyAllowedRecipient` only restricts the caller to the Hinkal contract (msg.sender check), not to a specific fund owner; `performHinkalChecks`/`dimensionsCheck`/`checkOnchainCreation` validate array-length consistency and calldata-hash integrity, but place no constraint on `op.value` versus any user-owned balance when `tokenNumber == 0`; `verifyWallet`'s signature check is bypassed entirely by choosing `signerAddress == address(0)`.

### Impact Explanation
Any ETH balance resident on `EmporiumUpgradeable` — from prior legitimate deposits/relay-fee flows, dust left behind by earlier operations, or ETH sent by other users — can be drained by an unprivileged attacker to an address they control, with a single self-authored, unsigned transaction. This is direct theft of ETH belonging to the protocol/other users, matching the **Critical** category (theft of shielded/in-flight user or protocol funds) since the funds being stolen are held under the Hinkal/Emporium trust boundary and the "proof" required to reach this path constrains nothing about ownership of the value moved. The attack is repeatable every time Emporium's ETH balance is non-zero, limited only by how much ETH happens to be resident there at call time.

### Likelihood Explanation
- Precondition: `EmporiumUpgradeable` must hold a non-zero ETH balance (plausible via `receive() external payable {}` at line 369, normal ETH-token external actions that route ETH through it as `externalAddress`, or accumulated dust).
- Attacker cost: one `Hinkal.transact` call with a self-generated proof for `tokenNumber = 0` — this is the cheapest, simplest possible Emporium call shape, requiring no nullifiers/UTXOs tied to the drained value.
- No privileged role, signature, or relayer cooperation is required (`signerAddress = address(0)` path).
- Feasible and repeatable at will whenever Emporium's ETH balance is positive.

### Recommendation
For the min-circuit / empty-`erc20TokenAddresses` path, either (a) forbid non-zero `op.value` for CASE 2 operations entirely when `erc20TokenAddresses.length == 0` (require `op.value == 0` unless routed through a signed `invokeWallet` call spending the user's own `HinkalWallet` balance), or (b) always compute ETH balance accounting in `runAction` regardless of `erc20TokenAddresses` contents (e.g., always track `address(this).balance` before/after and require the net change be accounted for/attributed to the caller via UTXO creation or an explicit non-min circuit that constrains ETH movement), and require `stack.signerAddress != address(0)` (i.e., mandatory signature verification) whenever any `op.value > 0` is present in the stack.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (proxy-initialized), register Emporium as external action id.
2. Seed Emporium with ETH (e.g., `vm.deal(address(emporium), 5 ether)` to simulate stranded/legitimate protocol ETH, or drive it through a normal ETH-token external action call that leaves residual balance).
3. As `attacker` (a fresh EOA with no UTXOs), generate a min-circuit proof for `dimensions.tokenNumber = 0` using the real circuit (`formInputEmporiumMin` public signals: `emporiumMessage`, `timeStamp`, `calldataHash`).
4. Build `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack({ops:[EmporiumOperation({endpoint: attacker, invokeWallet:false, value: 5 ether, callData: ""})], signerAddress: address(0), maxFee:0, deadline: block.timestamp+1000, v:0,r:0,s:0}))`, correct `calldataHash`.
5. Call `hinkal.transact(a,b,c,dimensions,circomData)` from `attacker`.
6. Assert: `emporium.balance` before minus after == 5 ether, and `attacker.balance` after minus before == 5 ether, while no `nullifiers`/UTXO ownership tied `attacker` to that 5 ether (assert `circomData.amountChanges.length == 0` and no revert from `BalanceChangeShouldBePositive`).

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
