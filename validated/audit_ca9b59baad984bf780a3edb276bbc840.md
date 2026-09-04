### Title
Shared `msg.sender` identity of `EmporiumUpgradeable`'s "stateless" call path lets any unprivileged user drain balances that third parties credit to Emporium's address - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract itself whenever an operation is a "stateless interaction" (`op.invokeWallet == false` or `stack.signerAddress == address(0)`). Because Emporium is one fixed, singleton-deployed contract shared by every Hinkal user, any external protocol that keys state (deposits, allowances, ownership, claims) to `msg.sender` will see the exact same principal — Emporium's address — regardless of which unprivileged user actually triggers the call, and the internal balance-diff logic in `runAction` will happily attribute whatever new tokens land on Emporium to *whoever* submits the next transaction.

### Finding Description
**Equality claimed to be broken:** the set of principals a third-party protocol trusts as "the controller behind `address(Emporium)`" (intended: only the specific depositing user, enforced nowhere on-chain) vs. the set of principals who can actually cause an Emporium-attributed call (in practice: any EOA that can build a valid Hinkal transaction routed through `runAction`).

Code path:
- `runAction` is gated only by `onlyAllowedRecipient`, which checks `msg.sender == Hinkal.sol` (a registered recipient), not any relationship between the caller and a specific prior depositor: [1](#0-0) 
- Inside `runAction`, for stateless ops the call executes with `msg.sender == Emporium`: [2](#0-1) 
- `verifyWallet` only enforces replay protection on `circomData.emporiumMessage` via a used-message nonce; it never checks that the caller is the same principal who previously deposited into the external protocol being called: [3](#0-2) 
- After the arbitrary external call(s) complete, the contract simply measures `balancesAfter - balancesBefore` and mints an outbound UTXO for that delta to whatever `stealthAddressStructure`/recipient the *current* caller supplied — with no linkage to who originally funded the external protocol: [4](#0-3) [5](#0-4) 
- The "stateful" path (`invokeWallet && signerAddress != 0`) routes through a per-signer `HinkalWallet`, which is `onlyEmporium`-gated and therefore isolates identity per signer address: [6](#0-5)  — but this isolation is **optional**; nothing forces `invokeWallet=true`/a non-zero `signerAddress` for any given op, so an attacker simply chooses `invokeWallet=false` to fall into the shared, singleton-identity path.
- The minimal "Emporium" ZK-circuit input path (`formInputEmporiumMin`) requires only `emporiumMessage`, `timeStamp`, `calldataHash` as public signals — it does not constrain which external protocol/account state the op is allowed to touch, confirming that ops are fully attacker-chosen: [7](#0-6) 

Root cause: Emporium's deployed address is a single, permanent, non-per-user identity used to call arbitrary third-party contracts on behalf of *anyone* who can submit a valid Hinkal transaction. Once any legitimate interaction causes a third-party protocol to record `msg.sender == Emporium` as the owner/depositor of some value (a lending position, a claimable airdrop, an approval, an `onlyOwner`-style role), that value becomes withdrawable/claimable by literally any subsequent unprivileged caller, because `runAction`'s balance-diff accounting attributes any resulting increase to whoever calls next, with no check tying the withdrawal back to the original depositor's proof/UTXO.

None of the existing guards address this: `onlyAllowedRecipient` only restricts the caller to `Hinkal.sol` itself (every user's transaction goes through Hinkal.sol, so this offers no per-user isolation); `verifyWallet`'s nonce check only prevents replaying the *same* signed message, not cross-user reuse of the shared identity; the balance-before/after check only prevents Emporium's balance from going negative, it does not verify provenance of a positive delta.

### Impact Explanation
Any value a third-party protocol has credited to `address(Emporium)` (lending collateral/deposits, staking positions, claimable airdrops, ERC20 allowances granted to Emporium, roles such as `onlyOwner`/`onlyAllowedRecipient` at that external protocol) can be drained/claimed by an unrelated, unprivileged attacker by crafting an Emporium op that calls `withdraw()`/`claim()`/any state-changing function on that protocol and directing the resulting balance increase to their own UTXO. This is a direct theft of funds that were legitimately routed through the protocol's own shared executor contract, matching the Critical bar ("direct theft of shielded or in-flight user funds" — the funds in flight through the external protocol via Emporium are stolen before ever returning to the rightful depositor). It is fully repeatable for every distinct pool of value any protocol accumulates under Emporium's identity, and costs the attacker only the gas/proof-generation for a single Hinkal transaction using their own UTXOs (which need not contain any of the stolen value).

### Likelihood Explanation
Preconditions: (1) some external protocol must whitelist/credit `address(Emporium)` as a trusted depositor/owner/recipient because a legitimate Emporium-mediated interaction occurred previously — this is a normal, expected usage pattern for a "call any DeFi protocol from your shielded balance" feature, not a contrived edge case; (2) the attacker needs no special role — any EOA that can generate a Hinkal transaction and craft `CircomData`/`EmporiumStack` with `invokeWallet=false` can exploit it. This requires no compromised keys, no relayer collusion, no protocol bugs outside this repo — only that a real external protocol (lending market, farm, distributor) treats `msg.sender` as an identity, which is standard Solidity practice. Given Emporium is explicitly designed to interact with arbitrary third-party protocols, this exposure is likely to materialize the moment Emporium is used against any protocol with persistent per-`msg.sender` state.

### Recommendation
Never let `runAction` execute an external call directly `from` the Emporium contract's own address when interacting with stateful third-party protocols. Force every op that isn't a simple stateless read/no-state-changing call to route through a **per-user** proxy/wallet contract (the existing `HinkalWallet` pattern), so that the identity seen by the external protocol is unique to the depositing user (e.g., a deterministic CREATE2 wallet keyed to the user's stealth/viewing key), not shared globally. At minimum, disallow the "stateless" `op.endpoint.call` branch for any endpoint that was previously used to accrue stateful balances, or require that value withdrawn from an external protocol via `runAction` can only be attributed to the same principal (proof-bound identity) that originally deposited it — e.g., by tracking, per external protocol+token, which stealth identity funded it and requiring later withdrawal proofs to reference the same identity/nullifier chain.

### Proof of Concept
Hardhat/Foundry test plan:
1. Deploy a `MockLendingPool` with `deposit(token, amount)` that does `balances[msg.sender][token] += amount` and `withdraw(token, amount)` that requires `balances[msg.sender][token] >= amount` and transfers `amount` of `token` to `msg.sender`.
2. Deploy `EmporiumUpgradeable`, `HinkalHelper`, and `Hinkal.sol`; register Emporium as `IExternalAction` with `HINKAL_EMPORIUM_ACTION_ID`; register `Hinkal.sol` as an allowed recipient of Emporium.
3. **Legitimate user A** performs a normal Hinkal transaction whose `EmporiumStack.ops` include a stateless op: `endpoint = MockLendingPool`, `callData = deposit(token, 1000)`, funded from A's own shielded UTXO (`deltaAmountChanges[i] < 0` for `token`). Assert `MockLendingPool.balances[address(Emporium)][token] == 1000` and A receives no output UTXO for `token` (funds are now "stuck" as external pool credit under Emporium's identity).
4. **Attacker (different unprivileged EOA)**, holding no relationship to A, no privileged role, and no knowledge of A's keys, builds their own Hinkal transaction with `deltaAmountChanges[i] == 0` for `token` (no deposit of their own) and an Emporium op: `endpoint = MockLendingPool`, `callData = withdraw(token, 1000)`, directing the output UTXO's `stealthAddressStructure` to attacker's own address.
5. Assert both sides of the equality:
   - Before: `MockLendingPool.balances[Emporium][token] == 1000` (credited to A via prior legitimate use).
   - After attacker's tx: `MockLendingPool.balances[Emporium][token] == 0`, `token.balanceOf(Emporium) `unchanged net`, and the attacker's decrypted UTXO output equals `1000` of `token` — i.e., funds A deposited land under the attacker's control, confirming `runAction`'s balance-diff/UTXO-mint logic (lines 132–151, 162–184 of `EmporiumUpgradeable.sol`) attributes third-party-protocol credit to whichever unrelated caller withdraws it next.
6. Confirm no existing check reverts the attacker's transaction: `onlyAllowedRecipient` passes (caller is `Hinkal.sol`), `verifyWallet`'s nonce check passes (different `emporiumMessage`), and `BalanceChangeShouldBePositive` does not trigger since Emporium's balance strictly increases during the call.

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

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L21-34)
```text
    modifier onlyEmporium() {
        if (msg.sender != emporium) {
            revert NotAllowedToCallWallet();
        }
        _;
    }

    function callHinkalWallet(
        address endpoint,
        bytes calldata data,
        uint value
    ) external onlyEmporium returns (bool success, bytes memory err) {
        (success, err) = endpoint.call{value: value}(data);
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
