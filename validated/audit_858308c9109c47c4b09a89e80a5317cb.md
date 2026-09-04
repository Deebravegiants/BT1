### Title
Duplicate `address(0)` (ETH) entries in `circomData.erc20TokenAddresses` let a single `msg.value` back multiple independent `amountChanges` legs, minting shielded ETH value without full backing - (File: `contracts/Hinkal.sol`)

### Summary
`Hinkal.transact` computes `oldBalances`/`newBalances` once for the whole `erc20TokenAddresses` array and then, inside the per-index loop, recomputes `balanceDif` by adding the *entire* `msg.value` for every index whose token is `address(0)`. Because the same global `msg.value` is re-added on every ETH-typed index rather than being consumed/split across duplicate entries, an attacker who lists `address(0)` twice can have the balance-equation check pass independently for each leg with a single deposit, allowing `amountChanges` for two ETH legs (2V) to be validated against only one real ETH deposit (V).

### Finding Description
Equality that should hold: `real ETH received by the contract in this call == sum(amountChanges over ETH-typed indices, excluding onChainCreation) + sum(utxoAmount over ETH-typed indices)`.

Code path, `contracts/Hinkal.sol`:
```solidity
uint256[] memory oldBalances = getBalancesForArray(circomData.erc20TokenAddresses); // line 78
...
uint256[] memory newBalances = getBalancesForArray(circomData.erc20TokenAddresses); // line 88
...
for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {           // line 97
    int256 balanceDif;
    if (circomData.erc20TokenAddresses[i] == address(0)) {
        balanceDif = int256(newBalances[i]) + int256(msg.value) - int256(oldBalances[i]); // lines 100-104
    }
    ...
    require(balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + int256(utxoAmount), ...); // lines 137-146
}
```
`oldBalances[i]` already includes `msg.value` because it is read after the payable `transact()` call has been credited, so for a single real deposit `V` with no other balance change, `balanceDif` correctly evaluates to `V` for one ETH leg. The bug is that this same derivation is duplicated verbatim for every index that equals `address(0)`, and `oldBalances`/`newBalances` are identical for both duplicate indices (they are just the same array value copied by index, not re-measured per leg). So if `erc20TokenAddresses = [address(0), address(0)]`, both index `i` and index `k` independently compute `balanceDif = V`, and both independently satisfy `balanceDif == amountChanges[i]` and `balanceDif == amountChanges[k]` when `amountChanges = [V, V]`.

There is no accumulator that tracks "how much of `msg.value` has already been attributed to an earlier ETH leg" and no dedup/uniqueness check on `erc20TokenAddresses` found in `HinkalHelper`'s `performHinkalChecks`/`dimensionsCheck` path. `_internalTransact` (lines 172-230) also does not prevent this: for each positive `deltaAmountChange` it calls `transferERC20TokenFromOrCheckETH(erc20, externalAddress, address(this), amountChanges[i])`, which for ETH only asserts `msg.value == _value` (line 118-121 of `Transferer.sol`) and, since `_to == address(this)`, performs no actual transfer. This check is per-call and stateless, so it happily re-validates `msg.value == V` against the *same* `V` twice, never checking that cumulative claimed ETH legs sum to at most the single `msg.value` actually sent.

Attacker's exact call: `transact()` with `erc20TokenAddresses = [address(0), address(0)]`, `amountChanges = [V, V]`, `onChainCreation = [false, false]`, `msg.value = V`, and a self-generated proof whose public inputs are consistent with two independent output UTXOs of amount `V` each for the ETH token (the Solidity-side balance/slippage checks do not constrain the circuit to treat duplicate ETH legs as one deposit, so as long as the circuit's own `inTotal + amountChanges === outTotal` per-leg constraint is satisfied per index — which it will be, since each index is checked independently against its own `amountChanges[i]` — the proof verifies).

### Impact Explanation
If exploitable end-to-end, this allows an attacker to have the Solidity balance-conservation check accept `2V` of claimed on-chain ETH movement while only `V` of real ETH ever entered the contract, letting them mint/withdraw shielded ETH UTXOs backed by half the claimed collateral. Repeated across transactions, this directly drains the pool's ETH backing for other depositors — a Critical, direct insolvency/theft class issue if the circuit's own constraints do not independently prevent listing the same token twice with independently-satisfiable per-leg totals.

### Likelihood Explanation
Preconditions are minimal and fully within an unprivileged attacker's control: they only need to construct `circomData` with a duplicated `address(0)` entry and a matching self-generated proof, and send `msg.value = V`. No special tree state, privileged role, or victim funds are required to trigger the divergence itself.

### Recommendation
Do not add the raw `msg.value` per ETH-typed index. Instead, consume `msg.value` at most once across the whole loop (e.g., subtract each ETH leg's positive attributed amount from a running `remainingMsgValue` and require it to reach exactly zero after the loop for all ETH-typed indices), or reject `circomData.erc20TokenAddresses` containing duplicate `address(0)` (and ideally duplicate ERC-20 addresses in general) in `performHinkalChecks`/`dimensionsCheck` before proof verification.

### Proof of Concept
Hardhat fork test plan:
1. Deploy Hinkal stack; fund attacker EOA with `V` ETH.
2. Build `circomData` with `erc20TokenAddresses = [address(0), address(0)]`, `amountChanges = [V, V]`, `onChainCreation = [false, false]`, `slippageValues = [0, 0]`, and generate a locally-produced proof whose circuit public inputs are consistent per-leg (`inTotal_i + amountChanges_i === outTotal_i` for i and k independently, using two output commitments of `V` each).
3. Call `transact(a, b, c, dimensions, circomData)` with `{ value: V }`.
4. Assert both `require`s at `contracts/Hinkal.sol` lines 111-114 and 137-146 pass for both loop indices.
5. Assert `address(hinkal).balance - balanceBefore == V` (only one `V` actually received) while `sum(circomData.amountChanges filtered by onChainCreation==false) == 2 * V`, and that two on-chain/off-chain commitments each worth `V` were inserted via `insertCommitments` — demonstrating `2V` of shielded value validated against `V` of real backing.

*Note: full confirmation requires cross-checking `circuits/MainEVMCircuit.circom`'s constraints on `amountChanges` (out of full read access in this session) to verify the circuit does not independently reject duplicate token indices; the Solidity-side balance/slippage checks in `contracts/Hinkal.sol` reviewed here do not prevent the described divergence.*