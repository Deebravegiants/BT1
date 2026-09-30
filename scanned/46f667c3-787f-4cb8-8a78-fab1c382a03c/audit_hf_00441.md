# [H] Malicious user can trick bridge into spending rune UTXOs

## Summary
Severity: High
Contest weight: 0.3080
Dataset id: 1863
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During outgoing rune transfers on the btc chain, the bridge logic checks which utxos can be used to spend value needed for the rune transfers (minimum dust 564 to associate with destination output and ”change” output, and tx fee). It skips the utxos having less than minimumDustThreshold because those are associated with incoming rune transfers. Unfortunately a malicious user can trick the bridge into using incoming rune transfers by associating a value of 10001 with a rune output. Since the constructed transaction will not have a runestone output, it means that the runes associated with that output will simply be lost and unclaimable by anyone, causing consequent losses for the bridge.
util_btc.go#L97-L99:
```go
for _, utxo := range utxos {
    value := StringToInt(utxo.Get("value"))
    if value <= minimumDustThreshold {
        continue // don't spend what is most likely to be a rune utxo
    }
}
```
Internal pre-conditions
External pre-conditions
Attack Path
1. Malicious user makes a transaction in which the output directed to bridge address and which will be the target of the rune transfer, has an associated value of 10001. The bridge will use that output at some point to pay for transaction fees, and will lose associated runes. The attacker does not lose anything since he is able to claim tokens on destination chain and roundtrip back on btc taking somebody else rune balance. As a result the bridge is insolvent in the targeted rune token.

## Recommendation
Consider checking if the candidate utxo is associated with a rune explicitely
