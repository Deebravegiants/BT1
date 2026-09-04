### Title
Front-run of a permissionless external claim/reward call locks funds in `EmporiumUpgradeable` forever - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction()` measures the value produced by a batch of external operations purely as `balancesAfter - balancesBefore` taken *inside* the same transaction. Just like Notional's `claimCOMPAndTransfer()`, if a third-party protocol exposes a permissionless "claim on behalf of X" function that anyone can call, an attacker can front-run the Emporium call to push that reward/refund directly into the Emporium contract before `balancesBefore` is snapshotted. The reward is then invisible to the diff computed by this transaction and can never be swept out, because any op that tries to transfer it out directly makes the balance diff negative and reverts.

### Finding Description
`runAction()` snapshots balances, runs the signed/unsigned ops, then computes the delta: [1](#0-0) [2](#0-1) 

Only `balanceChange = balancesAfter[i] - balancesBefore[i]` (adjusted for what was deposited into Emporium via `deltaAmountChanges`) is ever released, via `handleOut()`: [3](#0-2) 

If a stateless op (`op.endpoint.call(op.callData)`, executed with `msg.sender == Emporium`) targets a protocol with a permissionless "claim for holder" function (e.g. Compound's `claimComp(address holder, CToken[] cTokens)` which anyone can invoke on behalf of any holder, exactly as described in the referenced report), an attacker can call that permissionless function directly against the Emporium contract's address *before* the Emporium-mediated transaction lands. The reward lands in the Emporium contract in an earlier block, so it is already included in `balancesBefore` when `runAction()` executes and is never captured by `balanceChange`.

Critically, this value cannot be recovered afterwards: any op that attempts to transfer the stuck token balance out of Emporium directly (e.g. `token.transfer(recipient, amount)` called as `op.endpoint.call(op.callData)`) reduces the contract's own balance during the same transaction, driving `balanceChange` negative and triggering the explicit revert: [4](#0-3) 

So the only sanctioned exit path (`handleOut`) can never release a balance that predates the transaction's own snapshot, and any attempt to do so via a raw op reverts the whole call. The reward is permanently locked in the Emporium contract, exactly mirroring the `claimCOMPAndTransfer()`/`netBalance` bug in the external report: a value-bearing balance change caused by a third party is left outside the equality the contract uses to move funds ("value moved by [an] external action but not counted in the balance equation").

### Impact Explanation
Any COMP-like permissionless reward/refund the Emporium's whitelisted DeFi integrations expose becomes permanently unrecoverable once front-run this way — a permanent freezing of protocol/relay/user-controlled reward funds that were meant to flow back to the Hinkal user through `handleOut()`. This matches the "permanent freezing of user funds" / "temporary freezing" impact tier used in the accepted Sherlock finding, escalated to High because reward accrual is an integral, continuously-occurring part of protocol operation, not an edge case.

### Likelihood Explanation
Any EOA (no privileges required) can watch the mempool for a pending Emporium transaction whose ops interact with a protocol exposing a permissionless claim/refund function keyed to `address(this)` (the Emporium contract), and simply call that claim function first. This costs only gas and requires no special access, matching the "cost is low" criterion Sherlock's escalation ultimately accepted for the analogous COMP bug.

### Recommendation
Do not rely solely on a same-transaction before/after balance diff to decide what is released. Either:
- Track and release the full current token balance held by Emporium (net of what belongs to a specific pending in-flight operation) rather than only the delta accrued during the current call, or
- Add an explicit, permissioned sweep/rescue path that lets Emporium release balances that predate the current transaction without being blocked by the `BalanceChangeShouldBePositive()` guard, or
- Snapshot balances (or at least call the risky claim ops) atomically at the very start of the transaction bundle in a way that cannot be preceded by an attacker-controlled call in an earlier block, e.g. by having the claim itself be the first op and immediately zeroing/tracking any pre-existing balance before assuming all future gain is "new."

### Proof of Concept
1. Emporium integrates with a lending/rewards protocol `P` that has `claimReward(address holder)` callable by anyone, sending `P`'s reward token to `holder`.
2. A legitimate Hinkal user builds an `EmporiumStack` with an op: `endpoint = P`, `callData = claimReward(address(Emporium))`, intending `handleOut()` to forward the claimed reward to them.
3. An attacker observes this pending transaction (or simply monitors accrued rewards) and calls `P.claimReward(address(Emporium))` directly in an earlier block. The reward token balance of Emporium increases now.
4. The legitimate transaction executes: `balancesBefore` (`EmporiumUpgradeable.sol` line 85) already includes the reward the attacker caused to land. The op's own `claimReward` call now returns/transfers nothing new (already claimed).
5. `balanceChange` (line 132-134) is computed as 0 (or unaffected) for the reward token, so `handleOut()` (line 162-184) releases nothing for that token.
6. The reward tokens remain on the Emporium contract. Any subsequent attempt to add an op that transfers those tokens out directly makes `balanceChange` negative and reverts (line 141-144), so the funds are permanently stuck.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-90)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L162-184)
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

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
            circomData.stealthAddressStructure,
            circomData.timeStamp
        );
    }
```
