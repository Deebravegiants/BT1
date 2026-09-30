# [H] Nonce management vulnerability

## Summary
Severity: High
Contest weight: 0.4054
Dataset id: 1866
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The evmSend function in the bridge implementation is vulnerable to a Denial of Service (DoS) attack due to improper nonce management. When a transaction is front-run and reverts, the lastNonce variable is not updated, causing subsequent transactions to reuse an already used nonce. This leads to repeated failures, effectively halting the bridge's functionality.
1. Improper Nonce Handling in evmSend:
• The lastNonce for a target network is not updated when a transaction fails. hain_evm.go#L106
• Subsequent transactions reuse the stale lastNonce, leading to reverts due to the contract's nonces check. hain_evm.go#L88-L91
2. Contract-Level Nonce Validation:
• The bridge contract marks nonces as used after a successful or front-run transaction and update highest nonce. evm/Multisig.sol#L60-L62
• Reuse of a nonce results in reversion due to the contract's require(!nonces[nonce]) check. evm/Multisig.sol#L58
3. Faulty Logic in Nonce Calculation:
• The condition BiGte(BiFirst(lastNonce[transfer.Target]),nonce) assumes lastNonce is always up-to-date, which is not guaranteed after a failure. hain_evm.go#L89
Internal Pre-Conditions
• evmSend relies on lastNonce to calculate the next nonce.
• Transactions that fail due to front-running do not update lastNonce.
External Pre-Conditions
• An attacker front-runs the transaction by preemptively using the calculated nonce.
• The transaction reverts, leaving lastNonce stale.
Attack Path
1. The attacker observes the bridge transaction being broadcasted with a specific nonce.
2. The attacker front-runs the transaction by submitting their own with the same nonce.
3. The bridge transaction fails and does not update lastNonce.
4. Subsequent transactions from the bridge reuse the same nonce, repeatedly reverting.
5. The bridge becomes stuck, unable to process further transactions for the affected network.
This vulnerability allows a malicious actor to halt all bridge transactions for a specific EVM network, effectively rendering the bridge inoperable for that network. The issue constitutes a Denial of Service (DoS) attack, impacting users and disrupting cross-chain functionality.
Proof of Concept (PoC)
1. Set up a bridge instance and initiate a transfer to just one (bypassing to an attempt an EVM network.
2. Front-run the bridge transaction by submitting a transaction with the same nonce as the bridge.
3. Observe that the bridge transaction reverts due to the nonce being already used.
4. Initiate another transfer. Observe that the same nonce is reused, causing repeated reverts.
5. The bridge becomes non-functional for the target network.

## Recommendation
1. Ensure lastNonce is Always Updated:
• Update lastNonce[transfer.Target] immediately after fetching the highestNonce, even in the event of a failure.
Example Fix:
```go
defer func() {
    if err := recover(); err != nil {
        nonce := evmCall(rpc, "", msAddress, "highestNonce--uint256")[0].(*big.Int)
        lastNonce[transfer.Target] = nonce
        log.Println("Synchronized nonce after panic:", nonce)
    }
}()
```
2. Use highestNonce Directly from the Contract:
• Replace reliance on lastNonce with highestNonce from the contract to ensure nonce accuracy.
Fix Example:
```go
nonce := evmCall(rpc, "", msAddress, "highestNonce--uint256")[0].(*big.Int)
nonce = BiAdd(nonce, IntToBi(1)) // Always use the next available nonce
```
