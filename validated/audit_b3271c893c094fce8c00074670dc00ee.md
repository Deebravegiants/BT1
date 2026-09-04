### Title
Unauthenticated stateless ops in `EmporiumUpgradeable.runAction` drain any token held by the action, bypassing the `-deltaAmountChanges` balance invariant - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `stack.signerAddress == address(0)`, `EmporiumUpgradeable.runAction` executes attacker-supplied `op.endpoint.call(op.callData)` with `msg.sender == EmporiumUpgradeable` and with no signature check at all (`verifyWallet` returns immediately for `signerAddress == address(0)`) [1](#0-0) [2](#0-1) . The post-ops balance/UTXO-out invariant only iterates over `circomData.erc20TokenAddresses`, an array fully controlled by the caller, so any token that the attacker omits from that array is never balance-checked and can be moved out of the contract by the ops with zero constraint.

### Finding Description
The invariant that should hold is: *for every token moved by the action, `balanceChange[token] == -deltaAmountChanges[token] + (net effect of the ops)`, and this must be enforced for every unit of value that leaves the contract.* This is only checked for tokens present in `circomData.erc20TokenAddresses`:

```solidity
for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
    int256 balanceChange = int256(balancesAfter[i]) - int256(balancesBefore[i]);
    if (deltaAmountChanges[i] < 0) { balanceChange -= deltaAmountChanges[i]; }
    if (balanceChange < 0) { revert BalanceChangeShouldBePositive(); }
    UTXO memory utxoOut = handleOut(balanceChange, circomData, i);
    ...
}
``` [3](#0-2) 

`circomData.erc20TokenAddresses` and `deltaAmountChanges` are both attacker-supplied/derived arrays whose length and contents the attacker fully controls per transaction (the attacker chooses which tokens to declare) [4](#0-3) . Before this loop runs, `stack.ops` (also attacker-controlled, decoded from `circomData.externalActionData.externalActionMetadata`) are executed:

```solidity
if (op.invokeWallet && stack.signerAddress != address(0)) {
    (success, err) = IHinkalWallet(stack.signerAddress).callHinkalWallet(...);
} else {
    bytes4 selector = bytes4(op.callData);
    if (selector == IHinkalWallet.callHinkalWallet.selector ||
        selector == IHinkalWallet.doSendToRelay.selector) { revert UnauthorizedWalletCall(); }
    (success, err) = op.endpoint.call{value: op.value}(op.callData);
}
``` [5](#0-4) 

When `stack.signerAddress == address(0)` (the unsigned/stateless path), there is **no EIP-712 signature check at all**, only a one-time-use `emporiumMessage` nonce, which any unprivileged caller can freely pick [6](#0-5) . The only restriction on the call is that its selector isn't `callHinkalWallet`/`doSendToRelay`; the target `op.endpoint` and full `op.callData` are otherwise unrestricted, and because this is a plain `.call()` (not delegatecall), `msg.sender` seen by `op.endpoint` is `EmporiumUpgradeable` itself.

**Exploit**: an attacker calls `Hinkal.transact` with a valid proof for their own (possibly trivial/zero-value) UTXOs, setting:
- `circomData.externalActionData.externalActionId/externalAddress` = Emporium,
- `circomData.erc20TokenAddresses` = some unrelated token(s) they legitimately deposit (or an empty/degenerate array),
- `circomData.externalActionData.externalActionMetadata` decoding to an `EmporiumStack` with `signerAddress = address(0)` and one `op` where `endpoint = <strandedOrResidualTokenAddress>` and `callData = abi.encodeCall(IERC20.transfer, (attacker, strandedAmount))`.

Inside `runAction`, this op runs as `EmporiumUpgradeable.call(token.transfer(attacker, strandedAmount))`, directly moving the residual/stranded/in-flight token balance out of the contract to the attacker. Because that token address is **not** included in `circomData.erc20TokenAddresses`, it is never included in `balancesBefore`/`balancesAfter`, so the `balanceChange < 0` guard and the `-deltaAmountChanges` equality never see this transfer at all — the theft is completely outside the scope of the invariant the contract tries to enforce, and `Hinkal.transact`'s own balance-diff checks (`balanceDif == amountChanges[i] + utxoAmount`) are likewise scoped only to `circomData.erc20TokenAddresses` and never observe the stolen token [7](#0-6) .

I was not able to fully verify within the available context whether `externalActionMetadata` (and thus `stack.ops`) is committed to as a public input / `calldataHash` constrained by the ZK circuit; based on the contract-level selector check being the only constraint applied on-chain, and the design intent evidenced by `onlyAllowedRecipient`/nonce checks rather than circuit-side ops validation, the ops content appears to be trusted purely as calldata the caller supplies for their own transaction, not cross-checked against a specific fixed op list per token accounting.

### Impact Explanation
Any token balance sitting in `EmporiumUpgradeable` that is not one of the tokens the attacker chooses to list in `circomData.erc20TokenAddresses` — including stranded relay fees left behind when `circomData.relay == address(0)` in a prior transaction, refunds from swaps/routers, or funds mid-flight for another user's still-pending signed (`signerAddress != 0`) operation — can be transferred directly to the attacker with a single `Hinkal.transact` call, with zero on-chain accounting catching it. This is direct theft of protocol/relay/other-user funds parked in the action, matching **Critical: direct theft of shielded or in-flight user funds** (or at minimum High: theft of protocol/relay fees), and is repeatable for every token/residual balance that accrues in the contract over time.

### Likelihood Explanation
The only preconditions are: (1) some non-zero balance of an ERC20 (or ETH) sits in `EmporiumUpgradeable` that is not part of the current transaction's declared token set — a state that arises naturally from `relay == address(0)` fee "stranding," swap refunds, dust, or other users' in-flight multi-op flows; (2) the attacker can submit any valid `Hinkal.transact` call for their own funds, which is exactly the assumed unprivileged attacker capability. No signature, role, or relay whitelist is required for the `signerAddress == address(0)` path. Attacker cost is a single gas-paying transaction; the attack is fully repeatable whenever residual balance exists.

### Recommendation
Do not scope the post-op balance invariant to a caller-supplied token list. Either (a) restrict the stateless op path (`signerAddress == address(0)`) to a fixed allow-list of endpoints/selectors that cannot directly call arbitrary ERC20 `transfer`/`approve`, or (b) enumerate and check the balance delta for every token actually touched by the ops (not just attacker-declared ones), or (c) require the ops list and every token it can move to be committed as part of the ZK circuit's public inputs so the prover cannot freely choose calldata that moves tokens outside the declared/accounted set. Additionally, ensure `circomData.relay != address(0)` fee flows fully sweep any computed fee immediately, so no protocol value is ever left stranded in the action contract.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (as a registered external action), a mock `HinkalHelper`, and an ERC20 mock token `RESIDUAL`.
2. Seed the residual: mint `RESIDUAL` tokens directly to `EmporiumUpgradeable`'s address (simulating a prior stranded-fee/refund scenario) — assert `RESIDUAL.balanceOf(emporium) == seededAmount`.
3. As an unprivileged attacker EOA, generate a valid proof for a trivial transaction on their own UTXOs (e.g., depositing 0 or a small amount of an unrelated `DUMMY` token), with `circomData.erc20TokenAddresses = [DUMMY]` (excluding `RESIDUAL`), and `externalActionMetadata` encoding an `EmporiumStack{ signerAddress: address(0), ops: [ { endpoint: address(RESIDUAL), invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, seededAmount)) } ] }`.
4. Call `Hinkal.transact(...)`.
5. Assert: `RESIDUAL.balanceOf(attacker) == seededAmount` and `RESIDUAL.balanceOf(emporium) == 0`, while `-deltaAmountChanges` for `RESIDUAL` was never computed/nonzero (it isn't even in `circomData.erc20TokenAddresses`) — i.e., tokens left the action (`seededAmount`) while `-deltaAmountChanges[RESIDUAL]` (undefined/0) shows the invariant "tokens leaving == -deltaAmountChanges Hinkal sent" is violated.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L97-113)
```text
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

**File:** contracts/Hinkal.sol (L97-147)
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
            }
```

**File:** contracts/Hinkal.sol (L234-256)
```text
    function _externalTransact(
        CircomData calldata circomData
    ) internal returns (UTXO[] memory) {
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );

        int256[] memory deltaAmountChanges = new int256[](
            circomData.erc20TokenAddresses.length
        );
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            deltaAmountChanges[i] = _calculateDeltaAmount(circomData, i);
            if (deltaAmountChanges[i] < 0) {
                transferERC20TokenOrETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    uint256(-deltaAmountChanges[i])
                );
            }
        }
```
