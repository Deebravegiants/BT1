### Title
Unrestricted `approve()`/arbitrary call via `EmporiumOperation.callData` lets a signer drain any ERC20 balance held by `Emporium` that is not listed in `circomData.erc20TokenAddresses` - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction`'s "Stateless Interaction" branch executes `op.endpoint.call{value: op.value}(op.callData)` with a fully attacker-chosen `endpoint` and `callData`, only excluding the `callHinkalWallet`/`doSendToRelay` selectors. Nothing restricts `endpoint` to being a token contained in `circomData.erc20TokenAddresses`, and nothing restricts the call to be `approve` on a listed token. Because the post-execution balance invariant only iterates over `circomData.erc20TokenAddresses`, an attacker can approve/drain any other ERC20 balance the `Emporium` contract holds without tripping the check.

### Finding Description
`runAction` computes `balancesBefore`/`balancesAfter` only for the tokens the caller itself declares in `circomData.erc20TokenAddresses`: [1](#0-0) [2](#0-1) 

Inside the ops loop, the stateless branch performs an arbitrary low-level call from the `Emporium` contract's own context, with only the wallet-callback selectors blocked: [3](#0-2) 

Since `circomData.erc20TokenAddresses` is attacker-supplied metadata for a proof the attacker itself generates, an attacker can set `op.endpoint = <arbitrary ERC20 not in erc20TokenAddresses>` and `op.callData = approve(attackerControlledSpender, type(uint256).max)`. This is not `callHinkalWallet` or `doSendToRelay`, so it passes the selector check and executes as `IERC20(token).approve(spender, amount)` with `msg.sender == Emporium`. The invariant loop afterwards never inspects that token's balance, so the approval (and any subsequent `transferFrom` drain done outside this call, or in a following op, of any tokens the Emporium contract holds for that ERC20) is completely invisible to the balance-consistency check that is supposed to guarantee "what left Emporium == what the accounting says left".

This is the direct analog of the reported bug class ("user can approve any token"): the same unrestricted-`approve()`-target pattern, mapped onto Hinkal's balance equation - a value-moving action (`approve`, and the drain that follows it) that is not counted by the equality the contract enforces (`balanceChange` over `circomData.erc20TokenAddresses`).

### Impact Explanation
Any ERC20 balance sitting in the shared `Emporium` contract that is not part of the attacker's own declared `erc20TokenAddresses` array (e.g. leftover dust from rounding in other users' or relay's operations, tokens mistakenly sent to `Emporium`, or fee-token remainders) can be permanently approved to and stolen by an attacker, with zero effect on the balance checks that are meant to guard the protocol. This is theft/permanent freezing of funds not belonging to the caller, held by the shared external-action contract - meeting the High severity bar ("theft or permanent freezing of protocol/relay fees").

### Likelihood Explanation
Any unprivileged EOA can call `Hinkal`/`Emporium.runAction` with a self-crafted `EmporiumStack` and a valid EIP-712 signature over their own message (or `signerAddress == address(0)` to skip signature verification entirely), so no special privilege is required - only that `Emporium` currently holds some balance of a token the attacker knows is unlisted.

### Recommendation
Restrict stateless `EmporiumOperation.endpoint` calls so that any call selector matching `IERC20.approve`/`increaseAllowance`/`transfer`/`transferFrom` (or any state-mutating call to a token contract) is only permitted when `endpoint` is itself contained in `circomData.erc20TokenAddresses`, and make the pre/post balance invariant authoritative over the full set of tokens touched by the ops, not just the declared array - mirroring the original recommendation to only allow approvals of allowlisted tokens.

### Proof of Concept
1. Attacker calls Hinkal's external-action flow (`runAction` on `Emporium`), with `circomData.erc20TokenAddresses = [tokenA]` (some token they legitimately interact with) while `Emporium` currently also holds a balance of `tokenB` (dust/leftover from any earlier operation).
2. Attacker's `EmporiumStack.ops` contains one op: `invokeWallet = false`, `endpoint = tokenB`, `callData = abi.encodeWithSelector(IERC20.approve.selector, attackerSpender, type(uint256).max)`.
3. `runAction` executes `tokenB.call(callData)` from `Emporium`'s context at [4](#0-3) , granting `attackerSpender` unlimited allowance over `Emporium`'s `tokenB` balance.
4. The post-loop invariant only checks `tokenA`'s balance change, so this passes.
5. Attacker (via `attackerSpender`) calls `tokenB.transferFrom(Emporium, attacker, balance)` separately, draining `tokenB` entirely from `Emporium`, with no accounting catching the loss.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-144)
```text
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
```
