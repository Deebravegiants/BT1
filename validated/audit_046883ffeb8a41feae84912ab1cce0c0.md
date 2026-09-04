### Title
Unauthenticated `originalSender` field lets an attacker pull ERC20 tokens from any address that has approved Hinkal - ([File: contracts/external-actions/DepositOnChainUtxosExternalAction.sol])

### Summary
`DepositOnChainUtxosExternalAction.runAction` uses `circomData.originalSender` as the `_from` address in a `transferFrom`-style pull, but this field is not tied to `msg.sender` of the top-level `transact()` call the way the analogous deposit path in `Hinkal.sol` enforces.

### Finding Description
In the internal deposit path, `Hinkal._internalTransact` explicitly requires the depositing address to be the actual transaction sender: [1](#0-0) 
This binds any ERC20 pull (`transferERC20TokenFromOrCheckETH`) to `msg.sender`, i.e., the depositor authorizing the pull is the one submitting the call.

However, for the external-action deposit path used to create blocked/on-chain UTXOs, `DepositOnChainUtxosExternalAction.runAction` instead pulls funds from `circomData.originalSender`, a value read straight out of calldata with no check that it equals the real transaction sender or the top-level `msg.sender` who invoked `Hinkal.transact()`: [2](#0-1) [3](#0-2) 

The only structural constraint on this code path is that `deltaAmounts[i] == 0`: [4](#0-3) 
which means `Hinkal._externalTransact` performs no ERC20 movement itself for this token index (it only transfers when `deltaAmountChanges[i] < 0`): [5](#0-4) 
so the entire authorization burden for the pull is delegated to this external action, which trusts `originalSender` unconditionally as the token source. `onlyAllowedRecipient` only verifies the caller is the registered `Hinkal` contract: [6](#0-5) 
it does not verify who the real end user submitting the transaction is, nor that `originalSender` matches them.

This mirrors the report's bug class of "a `transferFrom` not authorised by the prover or signer": any caller who can produce a valid Hinkal proof (which only constrains nullifiers/commitments/balance deltas, not who is named in `originalSender`) can set `originalSender` to any address that has previously granted ERC20 allowance to the `Hinkal` contract (a very common state, since normal deposits require users to `approve` Hinkal), then have this external action call `transferERC20TokenFrom(token, victim, msg.sender, tokenTotal)`, stealing the victim's approved tokens into attacker-controlled UTXOs.

### Impact Explanation
This breaks the balance equation "value moved by Hinkal must be authorized by the address it is moved from" — an attacker can steal ERC20 tokens from any third party that has an outstanding allowance to the Hinkal contract, converting them into shielded UTXOs the attacker controls. This is a direct theft of user funds via an unauthorized `transferFrom`, matching the Critical impact category (direct theft of user funds via a transfer not authorised by the token owner).

### Likelihood Explanation
High, because: (1) approving the `Hinkal` contract for token allowances is the normal, expected user workflow before depositing, so many addresses will have nonzero allowance at any time; (2) the attacker does not need any privileged role — just the ability to submit a `transact()` call to Hinkal routing to this external action with `deltaAmounts[i] == 0` and `originalSender` set to the victim's address; (3) there is no on-chain check anywhere in `Hinkal.sol` or `DepositOnChainUtxosExternalAction.sol` binding `originalSender` to the actual caller.

### Recommendation
Require `circomData.originalSender == msg.sender` at the top of `Hinkal.transact()` (or equivalently enforce it inside `DepositOnChainUtxosExternalAction.runAction`, or bind `originalSender` into the ZK circuit's public inputs/`calldataHash` so it cannot be set independently of the transaction submitter), consistent with the existing "Deposit should come from the sender" check used in `_internalTransact`: [7](#0-6) 

### Proof of Concept
1. Victim `V` previously calls `approve(Hinkal, largeAmount)` on some ERC20 token `T` in order to make a legitimate deposit later.
2. Attacker `A` crafts a valid Hinkal transaction (with a valid proof for their own nullifiers/commitments/balances) that routes to `DepositOnChainUtxosExternalAction` as the external action, with:
   - `circomData.originalSender = V`
   - `circomData.erc20TokenAddresses = [T]`
   - `deltaAmounts[0] = 0` (satisfies the `runAction` check, and Hinkal itself performs no transfer for this index)
   - `externalActionMetadata` encoding UTXO amounts summing to `tokenTotal <= allowance(V, Hinkal)`
3. `Hinkal._externalTransact` calls `DepositOnChainUtxosExternalAction.runAction`, which executes:
   `transferERC20TokenFrom(T, V, msg.sender /* Hinkal */, tokenTotal)`
   pulling `tokenTotal` of `T` from `V` into the Hinkal contract, and mints new UTXOs for `A` (via `circomData.stealthAddressStructure` controlled by `A`).
4. `V` never signed or authorized this specific transaction; only a stale, unrelated ERC20 `approve` is exploited.

### Citations

**File:** contracts/Hinkal.sol (L177-187)
```text
            if (deltaAmountChange > 0) {
                require(
                    circomData.externalActionData.externalAddress == msg.sender,
                    "Deposit should come from the sender"
                );
                transferERC20TokenFromOrCheckETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    address(this),
                    uint256(circomData.amountChanges[i])
                );
```

**File:** contracts/Hinkal.sol (L237-242)
```text
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );
```

**File:** contracts/Hinkal.sol (L247-256)
```text
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

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L31-35)
```text
        address userAddress = circomData.originalSender;
        require(
            userAddress != address(0),
            "DepositOnChainUtxosExternalAction: Invalid originalSender"
        );
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L49-53)
```text
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L75-82)
```text
            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
```
