### Title
Emporium sweeps and mints UTXOs for any pre-existing/stray token balance to the first caller - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` computes the UTXO amount to mint for a caller from a raw `balanceAfter - balanceBefore` delta on the Emporium contract, with no accounting for *whose* funds produced a pre-existing balance. Any token balance that ends up sitting on the Emporium contract before a `runAction` call (e.g. dust left over from a partially-swept operation, a stuck/failed inner call, or tokens mistakenly transferred directly to the contract) is silently folded into the next unrelated caller's output UTXO. This mirrors the "Converter" report's second point: value left in a helper/converter contract that anyone can subsequently redeem.

### Finding Description
`runAction` snapshots balances before executing the caller-supplied `EmporiumOperation[]` calls, then computes the post-call balance and derives the amount to pay out via `handleOut`: [1](#0-0) 

The code explicitly acknowledges that `balanceChange` reflects funds that were on the contract *before* this particular call: [2](#0-1) 

And `handleOut` pays out (and mints a UTXO for) the *entire* positive `balanceChange`, regardless of whether all of it was actually produced by the current caller's own operations: [3](#0-2) 

Because `deltaAmountChanges` (the amount the circuit/prover committed to moving into Emporium) is only used to offset the *negative* case, any *extra* balance beyond what the current prover moved in is attributed entirely to that prover's output UTXO. If a prior transaction left tokens stranded on the Emporium contract — for instance, a stateless op that partially failed to forward funds out, or an inner call whose intermediate balance wasn't fully swept back to `msg.sender`, or simply an accidental direct ERC20 transfer to the Emporium address — the *next* caller who includes that token in `circomData.erc20TokenAddresses` will have that stray balance folded into their own `balanceChange` and will receive a UTXO backed by funds they never contributed. This breaks the equality the pool is supposed to preserve: the shielded UTXO issued to a user must be backed exactly by the value that user's own action moved in, not by unrelated leftover balance in the external-action contract.

### Impact Explanation
This allows an unprivileged EOA to claim tokens it did not deposit — a direct theft of value that legitimately belongs to whoever's transaction left it stranded on Emporium (or was accidentally sent there). This is a shielded-fund misattribution/theft rather than merely a self-inflicted loss, since the beneficiary is not the party whose funds became stuck.

### Likelihood Explanation
Likelihood is moderate: it requires either (a) a prior interaction leaving genuine residual balance on the Emporium contract (which the contract's own comments show is an anticipated code path, not a hypothetical), or (b) tokens being sent directly to the Emporium contract address, which is a normal ERC20 mistake vector, not an exotic assumption. No admin/relay/owner privileges are needed — a normal user simply needs to call `runAction` (via the Hinkal entrypoint) for a token that currently has a stray balance sitting on the Emporium contract.

### Recommendation
Track Emporium's per-token balances explicitly (or require the prover's committed `deltaAmountChanges` to exactly match the observed balance delta rather than treating any positive residual as belonging to the current caller). Any balance found to exceed what the current operation legitimately produced should be swept by a permissioned recovery function, not automatically minted into the current caller's UTXO.

### Proof of Concept
1. Some prior interaction (a stateless op whose inner call reverts before fully forwarding funds out, or a plain mistaken `transfer` to the Emporium contract address) leaves `X` tokens of `TOKEN` sitting on the `EmporiumUpgradeable` contract.
2. An unrelated user Bob calls `Hinkal.transact` → `_externalTransact` → `EmporiumUpgradeable.runAction` including `TOKEN` in `circomData.erc20TokenAddresses`, with `deltaAmountChanges[i] == 0` (i.e., he neither deposits nor withdraws `TOKEN` through his own ops).
3. `balancesBefore[i]` includes the stray `X`; after Bob's (unrelated) ops execute, `balancesAfter[i]` is unchanged or increased, so `balanceChange = X` (or more).
4. `handleOut` transfers `X` `TOKEN` to Bob (`msg.sender`, i.e., Hinkal) and creates a UTXO of amount `X` for Bob's stealth address — Bob has redeemed tokens he never deposited.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-151)
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
