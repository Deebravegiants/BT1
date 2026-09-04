### Title
Shared Emporium balance in CASE2 (stateless) operations lets any user steal another user's cToken-based position - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.runAction`'s CASE 2 "stateless interaction" branch executes `op.endpoint.call(op.callData)` directly from the Emporium contract itself (`msg.sender == Emporium`), so any external position built this way (e.g. `cToken.mint()`) is held on Emporium's own shared balance rather than being isolated per-user. Because `handleOut`/`Hinkal.transact()` credit any *positive* balance change on that shared contract to whichever caller's `stealthAddressStructure` is present in the current call, an attacker can redeem a victim's previously-minted cTokens and mint themselves a UTXO for the proceeds.

### Finding Description
The broken equality is: *"underlying redeemed from a cToken position == owned by the stealth address of the user who originally deposited to mint it."* Nothing in the contract enforces this; instead the accounting only asserts *"balance increase measured on Emporium during this call == UTXO amount minted to whoever is calling `transact()` right now."*

Trace:
1. Victim calls `transact()` → `_externalTransact` → `EmporiumUpgradeable.runAction` with a CASE2 op `{endpoint: cToken, invokeWallet:false, callData: mint(amount)}`. Since `invokeWallet` is false (or `signerAddress == 0`), the call goes through the `else` branch: `op.endpoint.call{value: op.value}(op.callData)` [1](#0-0) . This means `cToken.mint()` is invoked with `msg.sender == Emporium`, so `cToken.balanceOf(Emporium)` increases — a position owned by the Emporium contract as a whole, not by the victim specifically.
2. Any subsequent attacker can call `transact()` with `externalActionId` pointing to Emporium, `erc20TokenAddresses = [underlyingToken]` (the cToken itself never appears in the array, so it's invisible to `getBalancesForArray`), `onChainCreation[0] = true`, `amountChanges[0] = 0`, all-zero `inputNullifiers[0]`, and metadata `EmporiumStack{signerAddress: address(0), ops: [{endpoint: cToken, invokeWallet:false, callData: redeem(cTokenAmount)}]}`.
3. `verifyWallet` only checks `usedMessages[emporiumMessage]`; if `stack.signerAddress == address(0)` it returns immediately without any signature/ops verification [2](#0-1) , so the attacker fully controls `ops` with no authorization tying it to the victim's mint.
4. CASE2 executes `cToken.redeem(cTokenAmount)` from Emporium — this succeeds because Emporium genuinely holds the victim's cTokens; it burns them and credits the underlying to Emporium's own balance.
5. `handleOut` computes `balanceChange = balancesAfter[i] - balancesBefore[i]` (positive, the redeemed amount) and transfers it to `msg.sender`, which at that call depth is the `Hinkal` contract (the caller of `runAction`), then mints a `UTXO` with `circomData.stealthAddressStructure` — the attacker's own stealth address — for that amount [3](#0-2) .
6. Back in `Hinkal.transact()`, since `onChainCreation[i] == true`, the balance-diff check reduces to `balanceDif == 0 + utxoAmount`, which is self-consistently satisfied because both sides are computed from the actual runtime execution, not pinned by the ZK proof to any specific "authorized" amount [4](#0-3) . `checkOnchainCreation` only requires `amountChanges[i]==0` and zero nullifiers when `onChainCreation` is set — it does not verify ownership of the pre-existing Emporium balance being swept [5](#0-4) .

No existing guard (`performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation`, `verifyWallet`, `onlyAllowedRecipient`, `rootHashExists`, or `insertNullifiers`) ties a CASE2 stateless external call's effect to the specific prior depositor; they only validate internal self-consistency of the current transaction's own public inputs and proof. The design comment in the code itself (`// the only case when balanceChange can be < 0, when there were some funds on emporium before the call`) acknowledges that Emporium can carry balances across transactions, but only guards against balance decreasing, not against a stranger claiming a balance increase caused by draining someone else's leftover position.

### Impact Explanation
This is Critical direct theft of a victim's principal plus any accrued interest/rewards from a lending-style position (or any other DeFi position left in Emporium's own balance via a CASE2 op). The attacker mints a fully backed, private UTXO in their own stealth address without ever depositing the underlying value themselves — effectively stealing shielded value from another user, not merely front-running or griefing. It is repeatable against any user who uses CASE2 to build a persistent position at any protocol where holding a receipt token (cToken, aToken, LP token, etc.) constitutes ownership of redeemable value, as long as Emporium (not a per-user `IHinkalWallet`) is the token holder of record.

### Likelihood Explanation
Preconditions are realistic and require no privileged access: any Emporium user performing a lending/staking-style CASE2 interaction (`invokeWallet=false`) leaves the resulting receipt token balance on the Emporium contract itself. The attacker only needs to generate their own valid Hinkal proof (something any user can do for their own UTXOs) and target the redeem/withdraw call on the known receipt-token contract before the victim redeems it themselves. Cost is a single `transact()` gas fee; the attacker needs no special role, and the exploit is fully repeatable for every outstanding shared-balance position.

### Recommendation
Do not allow CASE2 (stateless, non-wallet) Emporium operations to interact with protocols that leave a persistent, fungible, non-time-locked receipt balance directly owned by the Emporium contract. Either (a) force all state-creating interactions (mint/deposit into external protocols) through CASE1's per-user `IHinkalWallet` so receipt tokens are held by an address unique to the depositor, or (b) require CASE2 ops to be atomic (deposit-then-immediately-consume in the same tx, verified via a pre/post allowlist of selectors), or (c) track per-position ownership explicitly (e.g., an internal ledger mapping stealth address → receipt-token balance) and require redeem calls to debit only the caller's own tracked balance.

### Proof of Concept
Foundry test outline:
1. Deploy `EmporiumUpgradeable`, a mock `cToken` (mintable/redeemable 1:1 with an underlying `ERC20`), and `Hinkal`/`HinkalHelper` wired together; register Emporium as an allowed external action.
2. Victim: build `CircomData` with `erc20TokenAddresses=[underlying]`, CASE2 op `{endpoint: cToken, callData: mint(amount)}`, `signerAddress=address(0)`; call `transact()` with a valid locally-generated proof and a real deposit of `amount` underlying. Assert `cToken.balanceOf(Emporium) == amount`.
3. Attacker (different EOA/stealth address, zero prior deposits): build `CircomData` with `erc20TokenAddresses=[underlying]`, `onChainCreation[0]=true`, `amountChanges[0]=0`, zero `inputNullifiers`, CASE2 op `{endpoint: cToken, callData: redeem(amount)}`, `stealthAddressStructure` = attacker's own; generate a valid proof for this configuration and call `transact()`.
4. Assert: `cToken.balanceOf(Emporium) == 0` after redeem, `underlying.balanceOf(Hinkal)` increased by `amount`, and a new on-chain UTXO commitment was inserted for the attacker's stealth address with `amount == amount` (equal to the victim's original principal) — while the victim's own private balance/UTXO for that position is unchanged/unspendable, proving the funds were stolen.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-316)
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

**File:** contracts/Hinkal.sol (L134-146)
```text
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
```

**File:** contracts/HinkalHelper.sol (L173-202)
```text
    function checkOnchainCreation(
        CircomData calldata circomData
    ) internal pure {
        bool isInternalTransaction = circomData
            .externalActionData
            .externalActionId == 0;

        for (uint i = 0; i < circomData.onChainCreation.length; i++) {
            if (circomData.onChainCreation[i]) {
                require(
                    !isInternalTransaction,
                    "onChainCreation not allowed for internal transactions"
                );
                require(
                    circomData.amountChanges[i] == 0,
                    "amountChanges must be zero when onChainCreation is true"
                );
                for (
                    uint j = 0;
                    j < circomData.inputNullifiers[i].length;
                    j++
                ) {
                    require(
                        circomData.inputNullifiers[i][j] == 0,
                        "inputNullifiers must be zero when onChainCreation is true"
                    );
                }
            }
        }
    }
```
