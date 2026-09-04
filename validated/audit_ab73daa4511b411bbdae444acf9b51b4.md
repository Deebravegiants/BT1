### Title
Relay flat fee can be silently zeroed by setting `feeStructure.feeToken` to a token not present in `erc20TokenAddresses` - ([File: contracts/Hinkal.sol])

### Summary
`_internalTransact` computes `flatFee` per-token by comparing `circomData.feeStructure.feeToken` to each entry of `circomData.erc20TokenAddresses`, but nothing on-chain or in the circuit enforces that `feeToken` actually be one of the tokens in that array. Since the caller who generates the ZK proof also fully controls `feeStructure` (it is only bound into `calldataHash`/self-consistency, not checked against `erc20TokenAddresses`), the attacker can pick a `feeToken` that matches none of the withdrawal tokens, forcing `flatFee = 0` for every loop iteration while `hasPaidToRelay` is still marked `true`.

### Finding Description
The broken equality is: `flatFee` actually deducted for the relay in `_internalTransact` (Hinkal.sol:192-195) should equal the `flatFee` the relay was contractually promised for servicing the withdrawal. This equality fails because the per-token match `circomData.feeStructure.feeToken == circomData.erc20TokenAddresses[i]` (Hinkal.sol:192-195) has no fallback or aggregate check requiring the match to occur for at least one `i`. If the attacker sets `feeStructure.feeToken` to any address absent from `erc20TokenAddresses`, the ternary resolves to `0` on every iteration of the loop: [1](#0-0) 

`relayFee` is still computed from `variableRate` alone (`recipientAmount = (10000 - variableRate) * (sumAbs - flatFee) / 10000; relayFee = sumAbs - recipientAmount;`), so some non-zero amount is still transferred to `circomData.relay`, and `hasPaidToRelay = true` is set unconditionally once `circomData.relay != address(0)`, satisfying the final `require(circomData.relay == address(0) || hasPaidToRelay, "relay not paid")` check (Hinkal.sol:226-229). Thus the on-chain contract has no way to verify that the promised flat fee was actually paid — it only checks that *some* relayFee (however small, driven purely by `variableRate`) was transferred.

The root cause is that `FeeStructure.feeToken` is fully attacker-controlled data passed straight through `CircomData`, and is only referenced inside the calldata/proof self-consistency hash — it is never checked for membership in `erc20TokenAddresses`, nor is there any relay signature or on-chain relay-side approval binding a specific `feeStructure` to a specific relay before the transaction executes. `performHinkalChecks` validates dimensions and root/nullifier data but does not appear (from the code paths located) to validate `feeStructure` semantics against `erc20TokenAddresses`.

Exploit flow: an unprivileged attacker deposits their own funds, builds their own UTXO/proof, and calls `transact()` themselves (self-relaying) with `circomData.relay` set to any real whitelisted relay address and `circomData.feeStructure.feeToken` set to an address not included in `circomData.erc20TokenAddresses`. The withdrawal executes normally, `hasPaidToRelay` is set true, but the flat-fee component of the relay's compensation is unconditionally dropped to zero for every output token, so the relay only ever collects the variable-rate cut.

### Impact Explanation
This lets the transaction originator unilaterally strip the flat-fee component owed to the relay for every relayed withdrawal, permanently denying that portion of protocol/relay fee revenue with no way for the relay or protocol to detect or prevent it on-chain. This matches the "High - theft or permanent freezing of protocol/relay fees" impact category. It is repeatable on every relayed transaction the attacker submits.

### Likelihood Explanation
Preconditions are minimal: the attacker only needs to generate a valid proof for their own UTXOs (something they are already permitted to do) and choose `feeStructure.feeToken` freely when constructing `CircomData`, plus name any currently whitelisted relay address in `circomData.relay`. No special role, signature from the relay, or privileged access is required, and the cost is simply the normal gas/proof-generation cost of a self-submitted withdrawal.

### Recommendation
Enforce that `feeStructure.feeToken` corresponds to an actual entry in `circomData.erc20TokenAddresses` (e.g., require the loop to find at least one match before allowing `hasPaidToRelay = true`), and/or bind `feeStructure` to an explicit relay-signed commitment (verified on-chain) so the caller cannot unilaterally choose fee terms that were never agreed to by the named relay.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, register a whitelisted relay `R` in `RelayStore`.
2. As attacker `A`, deposit funds and generate a valid withdrawal proof over `erc20TokenAddresses = [tokenX]`, with `amountChanges` reflecting a withdrawal, `circomData.relay = R`, and `circomData.feeStructure = {feeToken: tokenY (not in erc20TokenAddresses), flatFee: F>0, variableRate: V}`.
3. Call `transact(...)` as `A`.
4. Assert: (a) call succeeds and `hasPaidToRelay` path is taken (no revert on `"relay not paid"`); (b) relay `R`'s balance increase equals `sumAbs - recipientAmount` computed with `flatFee = 0`, i.e., strictly less than the amount it would receive if `flatFee = F` had been honored — proving `flatFee deducted != flatFee promised`.

### Citations

**File:** contracts/Hinkal.sol (L188-224)
```text
            } else {
                uint256 sumAbs = uint256(-deltaAmountChange);
                uint256 relayFee = 0;
                if (circomData.relay != address(0)) {
                    uint256 flatFee = circomData.feeStructure.feeToken ==
                        circomData.erc20TokenAddresses[i]
                        ? circomData.feeStructure.flatFee
                        : 0;

                    require(
                        sumAbs >= flatFee,
                        "Relay Fee is over withdraw amount"
                    );

                    uint256 recipientAmount = ((10000 -
                        circomData.feeStructure.variableRate) *
                        (sumAbs - flatFee)) / 10000;

                    relayFee = sumAbs - recipientAmount;

                    if (relayFee > 0) {
                        transferERC20TokenOrETH(
                            circomData.erc20TokenAddresses[i],
                            circomData.relay,
                            relayFee
                        );
                    }
                    hasPaidToRelay = true;
                }
                if (sumAbs - relayFee > 0) {
                    transferERC20TokenOrETH(
                        circomData.erc20TokenAddresses[i],
                        circomData.externalActionData.externalAddress,
                        sumAbs - relayFee
                    );
                }
            }
```
