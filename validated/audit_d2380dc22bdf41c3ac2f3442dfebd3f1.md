### Title
Undeclared ERC20 tokens held/received by Emporium's shared identity can be drained with zero accounting - (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` only measures and enforces balance conservation for tokens explicitly listed in `circomData.erc20TokenAddresses`, which is attacker-supplied and unconstrained by the circuit with respect to *which* tokens must be listed. An attacker can craft an `EmporiumStack` whose ops pull an arbitrary token (e.g., a reward/dust balance sitting on Emporium's shared address, or freshly harvested from a third-party protocol using Emporium's on-chain identity) and transfer it straight to their own EOA, while simply omitting that token from `circomData.erc20TokenAddresses` so it is never balance-checked.

### Finding Description
The claimed invariant is: for every token, `balanceChangeOfEmporium == -deltaAmountChanges[i]` (tokens leaving Emporium must equal what the attacker declared as withdrawn). This is enforced only inside the loop: [1](#0-0) 

which iterates strictly over `circomData.erc20TokenAddresses` — a caller-supplied array. `balancesBefore`/`balancesAfter` are likewise computed only `getBalancesForArray(circomData.erc20TokenAddresses)`: [2](#0-1) [3](#0-2) 

Meanwhile, the `ops` executed inside `runAction` are arbitrary low-level calls to any `endpoint` with any `callData` (only `callHinkalWallet`/`doSendToRelay` selectors are blocked in the stateless branch): [4](#0-3) 

Nothing constrains `op.endpoint`/`op.callData` to only touch tokens present in `circomData.erc20TokenAddresses`. So if a token address is simply never included in that array:
- It's excluded from `balancesBefore`/`balancesAfter`.
- It's excluded from the `balanceChange < 0` revert check.
- It's excluded from `handleOut`, so it never produces a legitimate UTXO either — the tokens just leave Emporium to wherever the op sent them (e.g., directly to `attackerEOA` via `token.transfer(attackerEOA, amount)` as an op), with the transfer executed under Emporium's own identity (`msg.sender == EmporiumUpgradeable`).

**Attacker call:** submit a `CircomData` whose `externalActionData.externalActionMetadata` decodes to an `EmporiumStack` with:
1. `op[0]`: `endpoint = victim-adjacent-vault`, `callData = harvest()` (or similar), pulling a reward/dust token to Emporium's own balance (msg.sender = Emporium).
2. `op[1]`: `endpoint = rewardToken`, `callData = transfer(attackerEOA, harvestedAmount)`.

`circomData.erc20TokenAddresses` (and therefore `deltaAmountChanges`) omits `rewardToken` entirely, so the reward-token movement is invisible to the only guard that exists (`BalanceChangeShouldBePositive`). `verifyWallet`, `performHinkalChecks`, `onlyAllowedRecipient`, and the circuit's `inTotal + amountChanges === outTotal` constraint all operate only on the declared token set and the shielded UTXOs being spent/created by the attacker — none of them assert anything about the full set of tokens Emporium's identity is capable of touching during the call.

### Impact Explanation
Any ERC20 balance sitting on, or transiently routed through, Emporium's shared on-chain identity that is not deliberately declared by the caller in `circomData.erc20TokenAddresses` can be moved to an arbitrary attacker-controlled address with no accounting check and no proof constraint over it. Because Emporium is a single shared contract used by all Hinkal users for external actions, any dust, unclaimed rewards, or protocol-side reward pools that accrue to Emporium's address (from any prior interaction, by any user) are exposed to theft by any unprivileged EOA that can submit a proof for a runAction with a crafted ops list. This is repeatable per-block for as long as such balances exist or can be re-generated (e.g. by chaining a harvest call before the exfiltration transfer in the same stack), and constitutes moving assets that were never authorized/declared by the acting party's own proof — matching the High severity bar ("executing calls or moving assets a wallet owner or prover never authorised"), escalating to Critical if the drained value is itself in-flight shielded UTXO balance temporarily resident on Emporium.

### Likelihood Explanation
Preconditions: (1) Emporium must hold, or be made to receive via an op, a token not declared by the attacker in `erc20TokenAddresses` — trivial to arrange since `ops` allow arbitrary calls to arbitrary endpoints; (2) attacker needs only a valid proof for their own (possibly zero-value) UTXO set and the ability to freely construct `CircomData`/`EmporiumStack`, both explicitly permitted to an unprivileged actor per the threat model. No special role, timing, or victim cooperation is required — the attacker can even self-fund the initial "harvest" step via a mock/attacker-deployed contract to demonstrate the same code path applies to any legitimately-held Emporium balance. Cost is a single transaction; the technique is fully repeatable.

### Recommendation
Do not let the caller choose which tokens are balance-checked. Either (a) restrict `op.endpoint`/token universe touched by an `EmporiumStack` to exactly the tokens enumerated in `circomData.erc20TokenAddresses` (e.g., by requiring pre-declaration of every token any op is allowed to move, with an allow-list check performed against decoded calldata targets), or (b) maintain and check a global reconciliation invariant across all tokens Emporium is known to hold before/after `runAction`, not just the attacker-declared subset, so that any undeclared token leaving Emporium's balance also reverts.

### Proof of Concept
Foundry test outline:
1. Deploy a mock `VictimVault` with a public `harvest()` that mints/transfers `rewardToken` to `msg.sender` (simulating a real reward pool crediting Emporium's address from a prior legitimate interaction, or simply pre-seed `rewardToken` balance directly on the Emporium proxy).
2. Deploy `rewardToken` (ERC20 mock).
3. Build `EmporiumStack.ops = [ {endpoint: victimVault, callData: harvest()}, {endpoint: rewardToken, callData: transfer(attackerEOA, harvestedAmount)} ]`.
4. Build `circomData` with `erc20TokenAddresses` containing only an unrelated token (or empty), `deltaAmountChanges` accordingly `0`/absent for `rewardToken`, and a valid proof for attacker's own (zero-value) UTXO operation.
5. Call `Hinkal._externalTransact` (or `runAction` directly under the `onlyAllowedRecipient` context) with this data.
6. Assert: `rewardToken.balanceOf(attackerEOA)` increases by `harvestedAmount`, `rewardToken.balanceOf(Emporium)` returns to pre-harvest level, transaction does **not** revert with `BalanceChangeShouldBePositive`, and `circomData.amountChanges`/`erc20TokenAddresses` never referenced `rewardToken` — demonstrating `tokens leaving Emporium == -deltaAmountChanges declared` is violated (LHS = `harvestedAmount`, RHS = `0`).

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-124)
```text
        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-144)
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
```
