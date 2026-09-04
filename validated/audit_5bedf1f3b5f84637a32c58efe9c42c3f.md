### Title
Stateless (CASE 2) Emporium operations create protocol-side positions attributed to the shared Emporium contract, letting any unprivileged user steal state left behind by another user's deposit — (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` executes CASE 2 ("Stateless Interaction") calls with `msg.sender == EmporiumUpgradeable` itself rather than a per-user wallet, and its balance-diff accounting (`getBalancesForArray(circomData.erc20TokenAddresses)`) only measures the underlying tokens explicitly listed by the caller for that single transaction. Any external position created on a third-party protocol using Emporium's address as the beneficiary (e.g. an aToken balance from `lendingPool.deposit(..., onBehalfOf=Emporium)`) persists in that protocol's storage and is not tied to the depositor in any way Hinkal enforces, so a later unprivileged caller can redirect that position's value to an address of their choosing via a second CASE 2 call (e.g. `lendingPool.withdraw(asset, amount, attackerRecipient)`), stealing it entirely outside of the UTXO/balance accounting.

### Finding Description
The broken equality is: *value attributable to the account that created the protocol-side position (the victim, via `deposit(..., onBehalfOf=address(this))`)* should equal *value later claimable through Hinkal's accounted flow by that same account*. Instead, any subsequent unprivileged Emporium caller can claim it.

Code path:
- `Hinkal.transact` → `_externalTransact` (`contracts/Hinkal.sol` lines 234-261) resolves `externalActionAddress` from `externalActionMap` and calls `IExternalActionV2(...).runAction(circomData, deltaAmountChanges)`. There is no restriction tying a specific external-protocol state (e.g. an aToken balance) to the depositor.
- `EmporiumUpgradeable.runAction` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol` lines 76-160) is gated only by `onlyAllowedRecipient`, which checks `msg.sender == Hinkal contract` [1](#0-0) , not who ultimately controls the `EmporiumStack`. Any caller of `Hinkal.transact` (with `externalActionId` pointing at Emporium) can supply an arbitrary `EmporiumStack`.
- CASE 2 fires whenever `!(op.invokeWallet && stack.signerAddress != address(0))`, which is trivially satisfied by setting `stack.signerAddress = address(0)` — this also skips the EIP-712 signature check entirely in `verifyWallet` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol` lines 302-316, early `return` when `signerAddress == address(0)`).
- In CASE 2, `(success, err) = op.endpoint.call{value: op.value}(op.callData)` executes with `msg.sender == EmporiumUpgradeable` [2](#0-1) . Only the selectors for `callHinkalWallet`/`doSendToRelay` are blocked — there is no allowlist of endpoints or functions, and no restriction that the call must not create/redeem third-party protocol positions belonging to Emporium's own address.
- The only accounting check afterward is a diff over `circomData.erc20TokenAddresses`, computed via `getBalancesForArray` (`contracts/Transferer.sol` lines 169-176), which only reads `IERC20(token).balanceOf(address(this))` for the tokens the *caller themselves* lists. It never inspects protocol-side receipt tokens (aTokens/cTokens/LP shares) nor funds sent to third-party `to`/`recipient` addresses supplied inside arbitrary `callData`.
- Crucially, the "Emporium Min" mode (`CircomDataBuilder.formInputEmporiumMin`, triggered when `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`) constrains only `emporiumMessage`, `timeStamp`, and `calldataHash` as public signals [3](#0-2) . This lets an attacker submit a transaction with an empty `erc20TokenAddresses` array, causing the balance-diff loop in `runAction` (lines 132-151) to execute zero iterations — there is no check whatsoever on the value moved by the CASE 2 call in this mode.

Exploit flow:
1. Victim (or victim's own tooling) submits `transact` with an `EmporiumStack` containing a CASE 2 op: `lendingPool.deposit(asset, amount, onBehalfOf=EmporiumUpgradeable_address)`. Underlying tokens move from Emporium's balance into the lending pool (balance-diff matches `-deltaAmountChanges`, so `runAction` passes normally), but aTokens are minted to Emporium's address, a state the balance loop never inspects.
2. Attacker (any unprivileged EOA holding no special role) submits their own `transact` with `externalActionId` pointing to the same Emporium instance, `erc20TokenAddresses = []` (Emporium Min mode) or including the underlying token with `deltaAmountChanges[i] >= 0` so no funds are required from the attacker, and a CASE 2 op `lendingPool.withdraw(asset, amount, to=attackerRecipient)`.
3. Because CASE 2 always executes with `msg.sender == EmporiumUpgradeable`, the lending pool burns Emporium's aTokens (created in step 1) and sends the underlying directly to `attackerRecipient`, bypassing Emporium's own balance entirely (funds never touch `address(this)`, so `balancesBefore == balancesAfter`, and no UTXO is even required to extract value).
4. The victim's shielded UTXO representing the deposit is untouched/unredeemed, and the underlying value is now in the attacker's arbitrary recipient address — a pure theft of state the protocol left in a shared, permissionlessly-callable contract identity.

None of the existing guards stop this: `onlyAllowedRecipient` only checks the caller is the Hinkal contract, not who crafted the `EmporiumStack`; `verifyWallet`'s signature check is skipped entirely when `signerAddress == address(0)`; `performHinkalChecks`/`verifyProof`/`rootHashExists`/`insertNullifiers` only validate the attacker's own proof/nullifiers/root over their own claimed inputs, not the third-party protocol state Emporium happens to hold; and the balance-diff/slippage checks in `EmporiumUpgradeable.runAction` and `Hinkal.transact` only look at Emporium's own balances of caller-declared tokens, which the exploit deliberately routes around via `to`/`onBehalfOf` parameters and/or an empty token array.

### Impact Explanation
Critical — direct theft of a shielded/committed user's protocol-side balance (the aToken position created by a stateless op) by an unrelated, unprivileged party, executing a call the depositor never authorized to be later drained by someone else. This is repeatable for every stateless CASE 2 deposit-style operation any user routes through the shared Emporium contract, against any lending/staking/vault protocol whose position-holder identity is `msg.sender` at deposit time (i.e. Emporium's own address) and which exposes a withdraw/redeem function with a caller-chosen recipient.

### Likelihood Explanation
Preconditions: Emporium registered in `externalActionMap` (standard deployment state), at least one prior CASE 2 deposit-style op executed against a protocol that mints a fungible receipt token/position to `msg.sender` (Emporium) rather than the depositor's own wallet. Attacker cost: one `transact` call with a self-generated proof over their own (possibly zero-value) UTXOs — no special role, no signature, no cooperation from anyone. This is highly feasible for any protocol integration the Emporium is used with that follows the common `deposit(..., onBehalfOf)` / `withdraw(..., to)` pattern (e.g. Aave-style lending pools), and is repeatable against every outstanding position left on Emporium's address.

### Recommendation
Do not allow CASE 2 (stateless) operations to leave persistent state attributable to the Emporium contract's own address across transactions. Options: (1) require that any CASE 2 call which could create durable third-party state (deposit/mint/stake-style calls) must be routed through a per-user `HinkalWallet` (CASE 1) so the resulting position belongs to that user's own wallet address, not the shared Emporium; (2) maintain an allowlist of endpoints/selectors permitted in CASE 2, excluding functions that mint transferable/withdrawable positions to `address(this)`; (3) track and account for non-`erc20TokenAddresses`-listed receipt tokens (e.g., require declaring and diffing every token whose balance the op could change, disallowing "Emporium Min" zero-token mode for calls that touch state-bearing endpoints); (4) enforce that within a single `runAction` invocation, any position opened via CASE 2 must be fully closed/accounted for balance-wise before the call returns, using an allowlist-based invariant rather than relying solely on `erc20TokenAddresses` balance diffs.

### Proof of Concept
Foundry test plan:
1. Deploy a mock ERC20 `Asset` and a mock `LendingPool` with `deposit(address asset, uint256 amount, address onBehalfOf)` (pulls `amount` from caller, mints internal accounting `balances[onBehalfOf] += amount`) and `withdraw(address asset, uint256 amount, address to)` (requires `balances[msg.sender] >= amount`, decrements it, transfers `amount` of `Asset` to `to`).
2. Deploy `EmporiumUpgradeable`, register it in `Hinkal.externalActionMap`, fund a victim address with `Asset` and let them deposit into Hinkal's shielded pool normally.
3. Victim: generate a valid snarkjs proof and call `Hinkal.transact` with `externalActionId` = Emporium, `EmporiumStack.signerAddress = address(0)`, one CASE 2 op = `LendingPool.deposit(Asset, amount, onBehalfOf=address(Emporium))`, with `erc20TokenAddresses = [Asset]` and matching negative `deltaAmountChanges`. Assert `LendingPool.balances(address(Emporium)) == amount` after the call.
4. Attacker (fresh unprivileged EOA with their own arbitrary/zero-value UTXO input): generate their own valid proof and call `Hinkal.transact` with `externalActionId` = Emporium, `erc20TokenAddresses = []` (Emporium Min mode) or non-conflicting tokens, `EmporiumStack.signerAddress = address(0)`, one CASE 2 op = `LendingPool.withdraw(Asset, amount, to=attackerRecipient)`.
5. Assert: `Asset.balanceOf(attackerRecipient) == amount` (attacker gained the full victim-deposited amount) while `LendingPool.balances(address(Emporium))` is now `0`, and the victim's original Hinkal UTXO/nullifier for the deposit was never spent by the attacker's transaction — proving the equality `asset_owner(pre-existing position) == beneficiary_of_withdraw` is violated (victim ≠ attacker) with no compensating check anywhere in `EmporiumUpgradeable.runAction` or `Hinkal.transact`.

### Citations

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
