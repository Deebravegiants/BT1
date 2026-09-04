### Title
Shared custodial balance in Emporium + CASE 2's `msg.sender == Emporium` lets an attacker drain other users' ERC4626 vault shares - (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction`'s CASE 2 "stateless" branch executes `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract, so any callee sees `msg.sender == Emporium`. Because Emporium is a single shared singleton used by every user of the protocol, any ERC4626-style vault where a user deposits with `owner == Emporium` pools shares under one address, and any later attacker can call `redeem`/`withdraw` with `owner = Emporium`, satisfying the vault's `msg.sender == owner` check and draining the shared balance to an address of their choosing.

### Finding Description
The equality that must hold is: *the `owner` argument of any state-changing call executed on behalf of a depositor must have been authorized by the depositor whose share is being spent.* Instead, in CASE 2: [1](#0-0) 

the call originates from the Emporium contract itself, so `msg.sender` inside any callee is always the Emporium address, independent of which end user originally funded the position. Any user (including the victim) who deposits into an ERC4626-style vault via a CASE 2 op with `owner = Emporium` mints shares to `vault.balanceOf(Emporium)`, a value shared across all users who ever routed a deposit through Emporium in this manner.

An attacker, using their own valid UTXO/proof (fully self-crafted per audit rules, including `CircomData`, `externalActionMetadata`, and the encoded `EmporiumStack`), submits a `transact` with a CASE 2 op `{endpoint: vault, callData: redeem(allShares, attackerAddress, Emporium)}`. Since `msg.sender == owner == Emporium`, the ERC4626 owner check passes trivially with no allowance, redeeming the *entire* pooled share balance—including the victim's contribution—to the attacker's chosen receiver.

The balance-accounting guard that would normally catch unauthorized outflows only inspects Emporium's own balance of `circomData.erc20TokenAddresses`: [2](#0-1) 

If the attacker sets `receiver` in the `redeem` call to an address other than Emporium (e.g., their own stealth address), the withdrawn underlying assets never touch Emporium's own balance, so `balanceChange` for that token stays `0`—no `BalanceChangeShouldBePositive` revert fires, and no UTXO is minted for the stolen value. The theft is entirely invisible to Hinkal's shielded-balance accounting.

None of the existing guards prevent this:
- `performHinkalChecks`'s `calldataHash` check only enforces that the attacker's submitted `circomData` (including their own crafted `externalActionMetadata`/`callData`) is internally self-consistent with their own proof - it says nothing about who is authorized to be the `owner`/`receiver` of a call to an arbitrary third-party contract: [3](#0-2) 
- `verifyWallet`'s EIP-712 signature check is skipped entirely whenever `stack.signerAddress == address(0)`, which is exactly the CASE 2 stateless path: [4](#0-3) 
- The ZK circuit only constrains the attacker's own `amountChanges`/nullifiers/commitments for their own deposit; it does not constrain the semantics of arbitrary third-party `callData` routed through `externalActionMetadata`.

### Impact Explanation
Critical - direct theft of a victim's (or any other Emporium user's) vault position. Any value pooled under `vault.balanceOf(Emporium)` by unrelated depositors via CASE 2 stateless ops is redeemable by any attacker who can construct a valid self-authorized CASE 2 op, with proceeds routed to an address of the attacker's choosing and no corresponding UTXO ever created, i.e., no accounting trace inside Hinkal.

### Likelihood Explanation
Preconditions: at least one prior deposit (by the victim or any user) into a shared ERC4626-like vault via a CASE 2 op with `owner = Emporium`, leaving a nonzero `vault.balanceOf(Emporium)`. This is a normal, expected usage pattern of the Emporium stateless flow, not an edge case. The attacker only needs their own funds/UTXO and full control over their own `CircomData`/`EmporiumStack` fields, which matches the given attacker capability model exactly. The attack is repeatable against any vault/token where Emporium accumulates a pooled position, and costs only gas plus a trivial deposit to obtain a valid proof.

### Recommendation
CASE 2 stateless calls must not be allowed to interact with contracts where Emporium's own address is treated as a shared custodial "owner"/"principal" for pooled positions (e.g., ERC4626 `redeem`/`withdraw`, or any call whose semantics key off `msg.sender` as an implicit balance owner). Either:
- Disallow CASE 2 (`msg.sender == Emporium`) calls to endpoints/selectors that use `msg.sender` as an owner/allowance check for pooled assets, restricting such interactions to CASE 1 (per-user `HinkalWallet` proxy, where `msg.sender` is the user's own stealth wallet, not the shared Emporium), or
- Track and enforce per-depositor share accounting inside Emporium itself so that a CASE 2 `redeem` can only draw down the balance attributable to the calling proof's own prior deposits, or
- Require that any receiver in CASE 2 calldata equal Emporium's own address so that the existing `balancesBefore`/`balancesAfter` accounting always captures the flow (closing the "assets bypass Emporium's balance" gap) — combined with enforcing per-user share isolation.

### Proof of Concept
Foundry fork/unit test plan:
1. Deploy a mock ERC4626 vault and `EmporiumUpgradeable` with a linked `HinkalHelper`/`Hinkal`.
2. Victim: performs a `transact` with a CASE 2 op `{endpoint: vault, callData: deposit(victimAmount, Emporium)}`, resulting in `vault.balanceOf(Emporium) == victimAmount` (plus any attacker deposit already made).
3. Attacker: performs their own trivial `transact` depositing `attackerAmount` similarly (CASE 2 `deposit(attackerAmount, Emporium)`), so `vault.balanceOf(Emporium) == victimAmount + attackerAmount`.
4. Attacker: submits a follow-up `transact` with CASE 2 op `{endpoint: vault, callData: redeem(vault.balanceOf(Emporium), attackerStealth, Emporium)}`.
5. Assert: call succeeds (no revert) despite attacker having no allowance from victim; assert `underlyingAsset.balanceOf(attackerStealth) >= victimAmount + attackerAmount` (i.e., strictly more than `attackerAmount`, proving victim funds were stolen); assert no UTXO was minted in Hinkal's UTXO set corresponding to the stolen `victimAmount` (verify via `handleOut`/emitted UTXO events showing `balanceChange == 0` for the underlying token because it bypassed Emporium's own balance).

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-151)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L313-316)
```text

        if (stack.signerAddress == address(0)) {
            return;
        }
```

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```
