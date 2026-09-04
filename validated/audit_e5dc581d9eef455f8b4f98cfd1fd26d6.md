### Title
Unsigned/unconstrained Emporium ops let an attacker grant themselves ERC20 approval over Emporium's held balances, bypassing the balance-diff invariant - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes an attacker-controlled list of "stateless" operations (`op.endpoint.call{value}(op.callData)`) whenever `stack.signerAddress == address(0)`, with **no signature check at all** in that branch of `verifyWallet`. Because the post-action balance check (`balanceChange`) only compares `balanceOf` snapshots, an attacker can craft an op that calls `approve(attacker, amount)` on any ERC20 token the Emporium contract holds instead of moving it, which leaves `balanceChange == 0` (no revert, no output UTXO), and then drain that balance in a second, completely separate transaction via `transferFrom`.

### Finding Description
The equality the protocol is supposed to enforce is: **tokens leaving Emporium in a transaction == `-deltaAmountChanges` Hinkal sent to it in that transaction**. This is enforced only through `balanceOf` deltas: [1](#0-0) 

`handleOut` only reacts to a change in `balanceOf(EmporiumUpgradeable)`; it has no concept of allowances. `verifyWallet` skips all authentication when `stack.signerAddress == address(0)`: [2](#0-1) 

And in that unsigned path, `runAction`'s "CASE 2: Stateless Interaction" performs a fully attacker-controlled external call to any `op.endpoint` with any `op.callData`/`op.value`, only blocking two specific selectors (`callHinkalWallet`, `doSendToRelay`): [3](#0-2) 

Neither `circomData.externalActionData.externalActionMetadata` (which decodes into this `EmporiumStack`/ops list) nor the target `op.endpoint`/`op.callData` is constrained by the ZK circuit's public inputs — `formInputNormal`/`formInputEmporiumMin` never include the metadata content, and `calldataHash` only proves internal self-consistency of attacker-supplied data, not that the ops are benign: [4](#0-3) 

**Attacker's call:** submit `Hinkal.transact` with a trivially valid proof for the Emporium action, where `externalActionMetadata` encodes `EmporiumStack{signerAddress: address(0), ops: [{endpoint: strandedToken, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)}]}`. `strandedToken` need not even appear in `circomData.erc20TokenAddresses`, so it is never subject to the `balanceDif`/`amountChanges` equality check in `Hinkal.transact`: [5](#0-4) 

**Exploit flow:**
1. Emporium accrues residual/stranded token balance from any prior in-flight action, dust, or refund (the contract is a shared singleton custodying funds transiently for all users' actions).
2. Attacker runs the above `transact` call; `approve` leaves `balancesBefore == balancesAfter` for that token, so `balanceChange == 0`, `handleOut` returns nothing, no UTXO is emitted, and Hinkal's per-token invariant loop never even inspects that token since it's absent from `erc20TokenAddresses`.
3. In a **separate transaction** (outside Hinkal entirely), the attacker calls `IERC20(strandedToken).transferFrom(EmporiumUpgradeable, attacker, amount)` using the standing approval, extracting funds that were never accounted for as `deltaAmountChanges` sent to the attacker.

Existing guards fail because: `verifyWallet`'s signature check is bypassed entirely by using `signerAddress = address(0)`; `BalanceChangeShouldBePositive`/`handleOut` only watch `balanceOf`, not `allowance`; and Hinkal's balance-diff invariant only covers tokens the attacker chooses to list in `erc20TokenAddresses`.

### Impact Explanation
Direct theft of shielded/in-flight user funds: any ERC20 balance sitting in the shared `EmporiumUpgradeable` contract (stranded/residual balances from other users' actions, dust, or refunds) can be captured by any unprivileged attacker via a self-granted `approve`, fully decoupled from the `deltaAmountChanges` the protocol believes it sent. This is repeatable against every token the contract ever holds and matches the Critical category "direct theft of shielded or in-flight user funds."

### Likelihood Explanation
No special preconditions beyond the attacker being able to submit one valid (even trivial/zero-value) proof through `Hinkal.transact` targeting the Emporium action with `signerAddress = address(0)` — a fully permitted, unprivileged usage pattern. Cost is a single gas-cheap transaction plus a follow-up `transferFrom`; the attack is repeatable whenever residual balance exists in the shared Emporium contract.

### Recommendation
Require the Emporium's stateless-operation path to also be authenticated (e.g., always require a valid EIP-712 signature bound to `msg.sender`/`originalSender`, not skip verification when `signerAddress == address(0)`), and/or restrict `op.endpoint`/`op.callData` to a whitelist that excludes `approve`/other allowance-granting calls on arbitrary ERC20s, and additionally track and forbid net allowance changes to non-Hinkal addresses during `runAction`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable`, a mock ERC20; seed `EmporiumUpgradeable` with a residual balance of the mock token (simulate a stranded balance from a prior action or a plain `transfer` to the contract).
2. Attacker (unprivileged EOA) crafts `CircomData` with `externalActionData.externalActionId = EMPORIUM_ID`, `externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [approve-call op]}))`, and a valid Groth16 proof for a trivial/no-op Emporium message (locally generated, per repo's circuit toolchain).
3. Call `hinkal.transact(...)`; assert it succeeds, assert `token.allowance(emporium, attacker) == type(uint256).max`, and assert `token.balanceOf(emporium)` is unchanged (equality "tokens leaving action == -deltaAmountChanges" superficially holds as `0 == 0`).
4. In a second transaction, attacker calls `token.transferFrom(emporium, attacker, residualBalance)`; assert it succeeds and `token.balanceOf(attacker) == residualBalance`, proving value left Emporium with no corresponding `deltaAmountChanges` ever recorded by Hinkal.

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L162-176)
```text
    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );
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
