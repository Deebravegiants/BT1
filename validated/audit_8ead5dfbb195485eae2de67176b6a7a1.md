### Title
Pre-existing/stray Emporium token balance can be stolen and laundered as a fake "deposit leftover" via the flawed `balanceChange -= deltaAmountChanges[i]` adjustment - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`runAction` snapshots Emporium's ERC20 balances once before the entire `ops` loop and once after, then "corrects" the raw delta by unconditionally adding back the declared deposit amount (`-deltaAmountChanges[i]`) whenever a deposit is declared for that token. Because this correction is applied blindly (it does not verify that the real balance increase actually came from the ops that pulled in the attacker's own funds, as opposed to funds that were already sitting in the contract), an attacker can combine a same-slot `CASE 2` op that extracts pre-existing/stray balance with a legitimate self-funded deposit of the same size to make the adjusted `balanceChange` non-negative, causing `handleOut` to mint them an extra UTXO backed by funds that never belonged to them.

### Finding Description
The claimed equality is:

`balanceChange (adjusted) == balancesAfter[i] - balancesBefore[i] - deltaAmountChanges[i]`, intended to represent "how much new value is available in Emporium and should be paid out to the user."

`balancesBefore` is captured as the very first statement of `runAction`, before `stack.ops` execute [1](#0-0) . Any balance already sitting on the Emporium contract (dust from a prior action, a mis-routed or delayed transfer, a bridge refund, or leftover relay-fee token) is folded into `balancesBefore` and therefore treated as "not new."

The `ops` loop lets the attacker execute arbitrary calls, including `CASE 2` "stateless" calls where `op.endpoint.call(op.callData)` is executed with `msg.sender == Emporium` [2](#0-1) . Nothing restricts this call to only touch funds the current proof declares — an attacker can point `op.endpoint` at the ERC20 token itself and set `op.callData = transfer(attacker, S)`, directly draining any pre-existing balance `S` held by Emporium to themselves, since Emporium is the token holder making the call.

After the loop, `balancesAfter` is taken and the adjustment is applied per token:
```solidity
int256 balanceChange = int256(balancesAfter[i]) - int256(balancesBefore[i]);
if (deltaAmountChanges[i] < 0) {
    balanceChange -= deltaAmountChanges[i];
}
if (balanceChange < 0) revert BalanceChangeShouldBePositive();
UTXO memory utxoOut = handleOut(balanceChange, circomData, i);
``` [3](#0-2) 

Attack call sequence for token `i` with pre-existing stray balance `S`:
- `op[0]` (CASE 2, attacker-crafted): `token.transfer(attacker, S)` — steals the stray balance. Real balance goes from `S` to `0`.
- `op[1]` (legitimate): attacker's own declared deposit pulls `D = S` of their own funds into Emporium (via their proof's `deltaAmountChanges[i] = -D`). Real balance goes from `0` back to `S`.

At the end: `balancesAfter[i] = S`, `balancesBefore[i] = S`, so raw `balanceChange = 0`. Since `deltaAmountChanges[i] = -S < 0`, the code does `balanceChange -= (-S) = S`. The check `balanceChange < 0` passes (it's `S`, not negative), and `handleOut` transfers `S` more tokens to the attacker [4](#0-3) . The attacker recovers their own `D=S` deposit (fine) but *also* extracts the stray `S` directly via `op[0]` — net theft of `S` beyond their own funds, all while the "equality" `balanceChange == -deltaAmountChanges[i]` holds numerically (both equal `S`).

Without the cover deposit, stealing `S` alone would make raw `balanceChange = -S`, and since no deposit is declared for that token the `< 0` branch doesn't fire, so the `revert BalanceChangeShouldBePositive()` at line 143 would correctly block it. It is specifically the unconditional "add back declared deposit" adjustment that neutralizes this protection when a same-slot legitimate deposit is present — nothing in `performHinkalChecks`, `verifyProof`, or the circuit constraints (`inTotal + amountChanges === outTotal`) constrain what the arbitrary `op.callData` in `CASE 2` actually does with pre-existing contract balance; those constraints only bind the shielded ledger, not on-chain calls.

### Impact Explanation
Direct theft of any ERC20 (or ETH) balance sitting in the Emporium contract from any source (airdrops, stray transfers, unclaimed dust, previously-unswept relay fees, delayed refunds) by an unprivileged attacker, disguised as their own legitimate deposit's output UTXO. This is repeatable every time stray balance accumulates on Emporium and matches Critical: direct theft of protocol/user funds held by the contract, executed through a value-conservation check that the attacker can satisfy numerically while diverting third-party value.

### Likelihood Explanation
Preconditions: Emporium must hold some non-zero balance of a token not currently "in flight" as part of any pending action (an airdrop, dust, stray transfer, or leftover fee balance). The attacker needs only to: (1) observe/predict such a balance, (2) craft a normal deposit transaction of their own funds for the same token, and (3) include an extra `CASE 2` op that calls `token.transfer(attacker, S)` before their deposit op executes. This requires no special role — only the ability to submit a self-funded deposit through the existing `runAction` flow with attacker-controlled `EmporiumStack.ops`, which the rules explicitly grant to the attacker. Cost is just the attacker's own deposit amount, which they get back, making the attack essentially free besides gas.

### Recommendation
Do not simply add back the declared deposit amount to the raw balance delta. Instead, verify per-token that the real balance genuinely increased by at least the declared deposit before the ops consumed/spent it, e.g., snapshot balances immediately before and after each op that is expected to source a deposit, or require that `balancesAfter[i] - balancesBefore[i] >= -deltaAmountChanges[i]` is derived from an actually-verified inbound transfer amount (e.g., using `SafeERC20`-checked pull with reconciliation) rather than trusting the aggregate delta across the whole loop. Alternatively, disallow `CASE 2` ops from targeting the declared `erc20TokenAddresses` directly for `transfer`/`transferFrom`-style calls unless explicitly and separately accounted for, or track balances before/after every individual op to detect any decrease that isn't attributable to the declared external interaction.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, initialize with a mock `IHinkalHelper` and allowed recipient (simulate Hinkal calling `runAction`).
2. Fund Emporium directly with `S` tokens of `TokenA` (simulate stray/airdropped balance), bypassing any deposit flow.
3. Construct `CircomData` with `erc20TokenAddresses = [TokenA]`, `deltaAmountChanges = [-S]` (attacker's own legitimate declared deposit of `S`).
4. Construct `EmporiumStack.ops`:
   - `ops[0]`: CASE 2, `endpoint = TokenA`, `callData = abi.encodeCall(IERC20.transfer, (attacker, S))`.
   - `ops[1]`: CASE 2, `endpoint = TokenA`, `callData = abi.encodeCall(IERC20.transferFrom, (attacker, address(emporium), S))` (attacker pre-approved Emporium), simulating the deposit inflow.
5. Call `runAction` (from the allowed-recipient address) with this data.
6. Assert: `balanceChange == -deltaAmountChanges[0]` (i.e., `== S`) at line 137 (instrument via event or return value).
7. Assert attacker's TokenA balance after the call `== S` net gain beyond their own deposited `S` returned as the output UTXO (i.e., attacker ends with `+S` extra tokens from Emporium's stray balance, verified by checking Emporium's TokenA balance returns to `0`/pre-attack baseline while attacker gained `S` in stolen funds plus their own `S` back via the UTXO transfer in `handleOut`).

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-91)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

        for (uint256 i = 0; i < stack.ops.length; i++) {
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
