### Title
Unrestricted stateless `EmporiumOperation` calls let an attacker drain a victim's stale ERC20 allowance to Emporium into the attacker's shielded balance - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `EmporiumStack.signerAddress == address(0)`, `verifyWallet` performs no authorization check beyond nullifying the `emporiumMessage` nonce, and `runAction`'s "stateless" branch executes `op.endpoint.call(op.callData)` with no restriction on which contract or which account's tokens are touched. An attacker can encode an op that calls `TOKEN.transferFrom(victim, address(Emporium), X)`, relying on a stale allowance the victim previously gave the Emporium contract (e.g. during a legitimate "Approve & Swap"), and the resulting balance increase is credited entirely to the attacker's shielded UTXO.

### Finding Description
The equality being relied upon by Hinkal's accounting is:
`balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount`
(`contracts/Hinkal.sol:137-146`). This is meant to guarantee that every unit of value credited to a newly created shielded/on-chain UTXO was actually supplied by the caller (via `amountChanges` deposit for internal transfers, or via tokens moved by the external action for `onChainCreation` outputs).

The break is upstream, in `EmporiumUpgradeable.runAction` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-160`):
- `verifyWallet` (`EmporiumUpgradeable.sol:302-316`) only enforces nonce replay protection when `stack.signerAddress == address(0)`; it returns immediately without checking any signature or whose funds are being moved.
- In the ops loop, when `stack.signerAddress == address(0)` (or `!op.invokeWallet`), execution falls to `op.endpoint.call{value: op.value}(op.callData)` (`EmporiumUpgradeable.sol:103-113`) with no allow-list on `op.endpoint` and no validation of the encoded call beyond rejecting the `callHinkalWallet`/`doSendToRelay` selectors.
- An attacker crafts `op.endpoint = TOKEN`, `op.callData = transferFrom(victim, address(Emporium), X)`. Because `msg.sender` inside that call is the Emporium contract, this succeeds if `victim` previously left an outstanding (e.g. infinite) approval to Emporium from any earlier legitimate flow.
- `balancesAfter - balancesBefore` for `TOKEN` increases by `X` purely from the victim's pulled allowance (`EmporiumUpgradeable.sol:122-144`). `handleOut` then forwards that `X` to `msg.sender` (Hinkal contract) and returns a `UTXO(X, TOKEN, circomData.stealthAddressStructure, ...)` that is fully attacker-controlled (`EmporiumUpgradeable.sol:162-184`).
- Back in `Hinkal.transact`, Hinkal's own balance of `TOKEN` increases by `X` (`balanceDif == X`). To pass the balance-equality require, the attacker sets `circomData.onChainCreation[i] = true` and `circomData.amountChanges[i] = 0` (required by `checkOnchainCreation`, `HinkalHelper.sol:173-202`, which forces `amountChanges[i] == 0` and `inputNullifiers[i][*] == 0` whenever `onChainCreation[i]` is true). This yields `RHS = 0 + utxoAmount(X) = X == balanceDif`, so the check passes with zero funds ever coming from the attacker.
- Note: the question's literal parameterization (`onChainCreation=false`, `amountChanges=[+X]`) does not satisfy the balance equation (`RHS` would be `2X` vs `balanceDif=X`) and would revert; the actually exploitable field combination is `onChainCreation[i]=true`, `amountChanges[i]=0`, which produces the same theft outcome the question describes.
- The resulting `UTXO` is inserted as an on-chain commitment via `createOnchainCommitment`/`insertCommitments` (`contracts/HinkalBase.sol`) using the attacker's own `stealthAddressStructure` and `onChainEncryptedOutput`, giving the attacker a spendable shielded balance of `X` `TOKEN` backed by the victim's stolen allowance rather than any real deposit by the attacker.

None of `performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation`, the ZK proof, or the circuit's `inTotal + amountChanges === outTotal` constraint prevent this: with no input UTXOs and `amountChanges[i]=0`, the circuit is trivially satisfiable with `inTotal = outTotal = 0` for that token, and the actual value transfer happens entirely inside the unconstrained, attacker-authored Emporium call.

### Impact Explanation
Critical — direct theft of a third party's funds. Any EOA that has ever granted (and not revoked) an allowance to the Emporium contract is exposed to having that allowance drained by an unrelated attacker, with the stolen tokens landing in the attacker's own shielded UTXO. This is repeatable against every victim with an outstanding allowance and up to the full size of that allowance, and is fully attacker-initiated (no relayer, admin, or victim cooperation required).

### Likelihood Explanation
The only precondition is that some user has left a non-zero, non-revoked ERC20 allowance to the Emporium contract (a realistic and common outcome of "Approve & Swap"-style flows, especially with infinite approvals). The attacker needs only: their own valid ZK proof for a trivial zero-input/zero-output-for-that-token transaction, ability to set `externalActionId` to Emporium, and full control over `EmporiumStack`/`CircomData` fields (all explicitly permitted to an unprivileged EOA per scope). No special role or secret is required, making this highly feasible and cheap (gas only) to execute.

### Recommendation
- Require `stack.signerAddress != address(0)` (i.e. always require an EIP-712 signature) for any op whose `callData` can move third-party funds, or otherwise cryptographically bind the "stateless" op set to a specific authorizing party who owns the funds being moved.
- Restrict the stateless `op.endpoint.call` path to a vetted allow-list of endpoints/selectors (e.g. DEX routers) that cannot execute arbitrary `transferFrom` calls on behalf of Emporium against arbitrary victims, or strip Emporium of any standing ERC20 allowances after each interaction (no infinite/lingering approvals).
- Alternatively, make Emporium track and only recognize balance increases that originate from `deltaAmountChanges[i] < 0` pre-funding by Hinkal or from operations explicitly signed by the account whose tokens moved.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, and a mock ERC20 `TOKEN`.
2. `victim` calls `TOKEN.approve(address(emporium), type(uint256).max)` as part of a simulated legitimate prior "Approve & Swap" and never revokes it. Mint `TOKEN` balance `X` to `victim`.
3. Attacker (no `TOKEN` balance, no approval) builds `CircomData` with `erc20TokenAddresses=[TOKEN]`, `amountChanges=[0]`, `onChainCreation=[true]`, `inputNullifiers=[[0]]`, `externalActionData.externalActionId` = Emporium id, `externalActionData.externalActionMetadata` = ABI-encoded `EmporiumStack{ signerAddress: address(0), ops: [EmporiumOperation{endpoint: TOKEN, invokeWallet: false, value: 0, callData: abi.encodeCall(TOKEN.transferFrom, (victim, address(emporium), X))}] }`, valid `emporiumMessage` nonce, attacker's own `stealthAddressStructure`/`onChainEncryptedOutput`.
4. Generate a valid Groth16 proof for this trivial CircomData (0 inputs, 0 off-chain outputs for the token) using the project's own snarkjs/circom setup.
5. Call `hinkal.transact(a, b, c, dimensions, circomData)` from attacker EOA.
6. Assert: tx succeeds; `TOKEN.balanceOf(victim)` decreased by `X`; `TOKEN.balanceOf(address(hinkal))` increased by `X`; a `NewCommitment` event is emitted encoding a UTXO of amount `X` for `TOKEN` under the attacker's stealth address — confirming `balanceDif (X) == onChainCreation? 0 : amountChanges (0) + utxoAmount (X)` was satisfied purely via the stolen allowance, with the attacker never spending or approving any of their own `TOKEN`.