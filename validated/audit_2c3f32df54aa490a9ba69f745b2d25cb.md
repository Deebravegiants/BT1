### Title
DepositOnChainUtxosExternalAction pulls tokens from attacker-supplied `originalSender` instead of the transact submitter, letting anyone drain any address's approval - (File: contracts/external-actions/DepositOnChainUtxosExternalAction.sol)

### Summary
`runAction` reads `userAddress = circomData.originalSender` — a field fully controlled by whoever submits the `transact` call — and uses it as the `from` argument of `transferERC20TokenFrom` for every ERC20 token in the batch. There is no check anywhere in this function (nor visible in the parts of `Hinkal.sol`/`HinkalHelper.sol` that I was able to inspect) binding `originalSender` to `msg.sender` of the outer `transact` call. An attacker can therefore submit their own valid proof/UTXO set while setting `originalSender` to any address that has previously approved this action contract, causing that victim's tokens to be pulled into Hinkal-controlled on-chain UTXOs that the attacker's own `stealthAddressStructure` (also attacker-controlled) can later claim.

### Finding Description
The invariant that should hold is: for every `transferFrom` executed on behalf of a `transact()` call, `from == msg.sender` (the account that actually authorized and paid for the transaction), i.e. only the real depositor's funds should move.

In `DepositOnChainUtxosExternalAction.runAction`:
```solidity
address userAddress = circomData.originalSender;
...
if (tokenAddress != address(0) && tokenTotal > 0) {
    transferERC20TokenFrom(
        tokenAddress,
        userAddress,
        msg.sender,
        tokenTotal
    );
}
``` [1](#0-0) 

`originalSender` is part of `CircomData`, which is attacker-supplied calldata for the `transact()` entrypoint. Nothing in `runAction` requires `userAddress == tx.origin`/`msg.sender` of the top-level `Hinkal.transact` call. The subsequent balance-accounting check in `Hinkal.sol` only verifies that the *aggregate* balance change of the Hinkal contract equals the minted UTXO total:
```solidity
require(
    balanceDif ==
        (circomData.onChainCreation[i] ? int256(0) : circomData.amountChanges[i]) +
            int256(utxoAmount),
    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
);
``` [2](#0-1) 

This check only validates *how much* moved into Hinkal, not *from whom*. Since the ERC20 tokens genuinely move from `userAddress` to `msg.sender` (Hinkal), this equality holds regardless of whose allowance was consumed — the check provides no protection against an arbitrary `from`.

Regarding the address(0)/native-token portion of the question: the native branch does skip `transferFrom` (`tokenAddress != address(0)` guard at line 75), but this is not exploitable to mint unbacked UTXOs, because `Hinkal.transact` independently computes `balanceDif` for the `address(0)` entry as `newBalance + msg.value - oldBalance` and enforces the **exact** equality `balanceDif == utxoAmount` (not merely the `slippageValues[i]` floor). Since no ETH transfer happens inside the action, the only way `balanceDif` can equal a positive `utxoAmount` is if the attacker actually sends that much `msg.value` with the top-level call. A negative `slippageValues[i]` only relaxes the `>=` floor check; it does not relax the separate strict equality check, so minting `address(0)` UTXOs without real ETH backing is blocked by this second `require`. That specific claim in the question is therefore not exploitable as described.

The exploitable path is the ERC20 branch: `from = circomData.originalSender` with no binding to the real caller.

### Impact Explanation
Any address that has ever granted an ERC20 `approve` to the `DepositOnChainUtxosExternalAction` contract (a normal, expected step for legitimate users depositing on-chain UTXOs through this action) becomes drainable by any other, unrelated user. The attacker crafts their own valid proof/circuit inputs (their own nullifiers, own `stealthAddressStructure`), but sets `circomData.originalSender` to the victim's address. The victim's approved tokens are pulled into Hinkal and minted as on-chain UTXOs whose stealth address belongs to the attacker, giving the attacker full spend rights over the stolen funds. This is direct theft of a third party's tokens through Hinkal, matching the Critical severity category ("direct theft of shielded or in-flight user funds").

### Likelihood Explanation
- Precondition: the victim must have an outstanding ERC20 allowance to the `DepositOnChainUtxosExternalAction` contract address. This is a realistic precondition since users interacting with this specific action are expected/instructed to `approve` it before depositing.
- Attacker cost: normal gas cost of a `transact()` call with a self-generated valid proof; no privileged role required.
- Repeatable against every victim with a live allowance, until the allowance is exhausted or revoked.

### Recommendation
Bind `circomData.originalSender` to the true transaction submitter for actions that perform `transferFrom` on it — e.g., require `circomData.originalSender == msg.sender` of `Hinkal.transact` (propagated through `performHinkalChecks`/`CircomData`), or better, always source the `from` of `transferFrom` from the verified top-level caller rather than an unconstrained calldata field. Alternatively, constrain `originalSender` as a public input in the circuit and cryptographically tie it to the prover's key/signature so it cannot be set to an arbitrary third-party address.

### Proof of Concept
Foundry test plan:
1. Deploy Hinkal, `DepositOnChainUtxosExternalAction`, and a mock ERC20.
2. Victim (`v`) calls `token.approve(depositAction, 1000)`.
3. Attacker (`a`, unrelated EOA) builds `CircomData` with `originalSender = v`, `erc20TokenAddresses = [token]`, `externalActionMetadata` encoding `utxoAmounts = [[1000]]`, `stealthAddressStructure` = attacker's own keys, and a locally generated valid proof for the attacker's own (possibly zero-value) input/output UTXOs such that `amountChanges[0] == 0`/`onChainCreation[0] == true` and `deltaAmounts[0] == 0`.
4. Attacker calls `Hinkal.transact(...)` from account `a`.
5. Assert: `token.balanceOf(v)` decreased by 1000, `token.allowance(v, depositAction)` decreased by 1000, and a new on-chain UTXO commitment for 1000 tokens under the attacker's `stealthAddressStructure` was inserted — i.e., `from` of the executed `transferFrom` (`v`) != `msg.sender` of the `transact` call (`a`), demonstrating the broken invariant.

### Citations

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L31-82)
```text
        address userAddress = circomData.originalSender;
        require(
            userAddress != address(0),
            "DepositOnChainUtxosExternalAction: Invalid originalSender"
        );

        uint256[][] memory utxoAmounts = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (uint256[][])
        );
        require(
            utxoAmounts.length == tokenCount,
            "DepositOnChainUtxosExternalAction: metadata length mismatch"
        );

        utxoSet = new UTXO[](countUtxos(utxoAmounts));

        uint256 utxoIndex = 0;
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );

            address tokenAddress = circomData.erc20TokenAddresses[i];
            uint256 tokenTotal = 0;

            for (uint256 j = 0; j < utxoAmounts[i].length; j++) {
                uint256 amount = utxoAmounts[i][j];
                require(
                    amount > 0,
                    "DepositOnChainUtxosExternalAction: UTXO amount must be positive"
                );
                tokenTotal += amount;

                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
            }

            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
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
