### Title
Unrestricted `EmporiumOperation.endpoint`/`callData` lets an attacker grant a standing ERC20 approval from `EmporiumUpgradeable`, enabling later theft of any token balance the action holds - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction` executes an attacker-supplied list of `EmporiumOperation`s via arbitrary low-level calls (`op.endpoint.call{value: op.value}(op.callData)`) with no whitelist on `op.endpoint` and no filtering of `callData` selectors other than blocking `IHinkalWallet` selectors. An attacker can therefore make the Emporium contract itself `approve()` an attacker-controlled address for `type(uint256).max` on any ERC20 token, creating a persistent allowance that lets the attacker drain any current or future balance of that token sitting in the action contract — completely outside of Hinkal's `-deltaAmountChanges` accounting.

### Finding Description
The invariant the question asks about is: *tokens leaving the action in a tx == `-deltaAmountChanges` Hinkal sent it that tx*. The `runAction`/`handleOut` before/after balance-diff logic does correctly enforce this **for token transfers that occur inside the `runAction` call itself** [1](#0-0) , and pre-existing dust is properly excluded from `balanceChange` because it is present in both `balancesBefore` and `balancesAfter` and cancels out in the subtraction [2](#0-1) .

However, the invariant is broken **outside the transaction boundary**. The stateless-interaction branch of the operation loop performs a completely unrestricted external call:

```solidity
(success, err) = op.endpoint.call{value: op.value}(op.callData);
``` [3](#0-2) 

`op.endpoint`, `op.value`, and `op.callData` are all decoded directly from `circomData.externalActionData.externalActionMetadata`, which is fully attacker-controlled (the attacker signs their own `EmporiumStack` via `verifyWallet`, or can even leave `signerAddress == address(0)` to skip signature verification entirely) [4](#0-3) . The only restriction is a selector check against `IHinkalWallet.callHinkalWallet`/`doSendToRelay` — there is no restriction on the target address (no router allowlist) and no restriction on the called function.

Exploit flow:
1. Attacker crafts a valid Hinkal proof for their own small deposit (e.g. 1 wei of an arbitrary ERC20 token `X`), calling `Hinkal.transact` with `externalActionId` pointing at `EmporiumUpgradeable`.
2. In `externalActionMetadata`, the attacker encodes an `EmporiumStack` whose single operation is `op.endpoint = X`, `op.callData = abi.encodeWithSelector(IERC20.approve.selector, attackerAddress, type(uint256).max)`.
3. `runAction` executes this call from the Emporium contract itself (`address(this)` = Emporium), granting `attackerAddress` an unlimited standing `allowance` on token `X` from the Emporium contract.
4. `handleOut` only moves `balanceChange` (the amount matching this tx's `-deltaAmountChanges`) back to Hinkal; it never revokes or is aware of approvals granted during `ops` execution [2](#0-1) . The transaction completes successfully, satisfying all of Hinkal's on-chain checks (`balanceDif == amountChanges + utxoAmount`, slippage, nullifier insertion) because those checks only look at net balance changes, not at approvals granted.
5. At any later point in time — completely outside of Hinkal, with no proof, no `onlyAllowedRecipient` gate, no nullifier — the attacker calls `X.transferFrom(EmporiumAddress, attacker, X.balanceOf(EmporiumAddress))` directly on the ERC20 contract, sweeping out **any** balance of token `X` the Emporium contract holds at that moment: leftover dust from the attacker's own transaction, protocol residue from unrelated victims' swaps (slippage remainders, rounding dust, aggregator refunds), or even funds transiently present due to another user's in-flight `transact()` call for that token (since the deposit-in transfer in `Hinkal._externalTransact` happens before `runAction` and any balance present in the contract during that window is drainable by the standing approval) [5](#0-4) .

None of the existing guards prevent this: `performHinkalChecks`/`verifyProof` only validate the shielded-pool bookkeeping for the attacker's own UTXOs, `onlyAllowedRecipient` only checks that `msg.sender` (Hinkal) is calling `runAction`, and `verifyWallet`/EIP-712 signature checks only apply when `stack.signerAddress != address(0)` and are irrelevant to arbitrary stateless `ops`. There is no allowlist of routers/endpoints and no post-execution revocation of approvals granted by `ops`.

### Impact Explanation
This is a persistent backdoor: once granted, the attacker can drain any ERC20 balance of the approved token that the `EmporiumUpgradeable` contract holds at any time in the future, with zero additional cost. This directly matches the Critical category — theft of shielded/in-flight or protocol/other-users' funds parked in the action, entirely bypassing the `-deltaAmountChanges` accounting that is supposed to bound what leaves the action. The exploit is trivially repeatable for every ERC20 token the attacker wishes to target and requires only one cheap deposit transaction to set up.

### Likelihood Explanation
Preconditions are minimal: the attacker only needs the ability to call `Hinkal.transact` with a valid proof for a small deposit of their own (any amount, even the minimum unit), and to encode `externalActionMetadata` as an `EmporiumStack` with a single stateless operation. No privileged role, no victim key, and no special protocol state is required. Cost is a single small-value transaction plus gas. This is fully within the described "unprivileged attacker" capabilities (craft `CircomData`, `externalActionMetadata`, choose ordering/fields).

### Recommendation
- Restrict `EmporiumOperation.endpoint` to a contract-owner-managed allowlist of approved routers/protocols (similar to a router allowlist pattern), rejecting calls to arbitrary addresses.
- Disallow `callData` whose selector is `IERC20.approve`, `increaseAllowance`, `permit`, or any other approval-granting function on tokens the action can hold, or alternatively force all router approvals to be scoped/reset to zero at the end of every `runAction` call.
- As a stronger structural fix, avoid persistent allowances altogether: use only `transfer`/`safeTransfer` push patterns from the action, or scope approvals with a wrapper that revokes them within the same transaction after use (e.g., approve exact amount right before the swap call and reset to 0 immediately after, all inside `runAction`, never leaving a non-zero allowance outstanding after the call returns).

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (as a registered external action), a mock ERC20 `TokenX`, and give `EmporiumUpgradeable` some initial balance of `TokenX` (simulate protocol dust, e.g. `deal(address(tokenX), address(emporium), 100e18)`).
2. As `attacker`, construct a minimal valid Hinkal deposit proof/`CircomData` (1 wei of `TokenX`, `externalActionId` = Emporium's id, `signerAddress = address(0)` to skip signature checks) with `externalActionMetadata` encoding an `EmporiumStack` containing one `EmporiumOperation{ endpoint: address(tokenX), invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max) }`.
3. Call `hinkal.transact(a,b,c,dimensions,circomData)` and assert it succeeds.
4. Assert `tokenX.allowance(address(emporium), attacker) == type(uint256).max`.
5. As `attacker`, call `tokenX.transferFrom(address(emporium), attacker, tokenX.balanceOf(address(emporium)))` in a separate, unrelated transaction (no Hinkal call).
6. Assert `tokenX.balanceOf(attacker) >= 100e18` (the pre-existing dust that was never part of any `-deltaAmountChanges` Hinkal sent to the action), proving that value left the action without a corresponding decrease recorded via Hinkal's `amountChanges`/`deltaAmountChanges` accounting — breaking the stated invariant.

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

**File:** contracts/Hinkal.sol (L244-256)
```text
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
