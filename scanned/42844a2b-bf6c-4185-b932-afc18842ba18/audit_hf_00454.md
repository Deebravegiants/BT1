# [M] If utxo split for rune transfer

## Summary
Severity: Medium
Contest weight: 0.1336
Dataset id: 1880
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Rune transfers can be split into multiple edicts, and if that happens they will be indexed as separate transfers for the same transaction. Runemine handles this by aggregating them back into one amount by tx and rune, but if the query window is full (2500), some of those transfers may be truncated and left out.
The amounts are aggregated, but only for one query window:
```go
chain_btc.go#L16-L17:
transfers := NJ(HttpVal("GET", Env("INDEXER", "")+"/transfers?limit=2500&to="+ms, "", nil)).GetA("transfers")
for _, transfer := range transfers {
```
```go
chain_btc.go#L57-L62:
total := StringToBi("0")
for _, t2 := range transfers {
    if t2.Get("tx") == transfer.Get("tx") && t2.Get("rune") == transfer.Get("rune") {
        total = total.Add(total, StringToBi(t2.Get("amount")))
    }
}
```
Internal pre-conditions
External pre-conditions
Attack Path
User loses part of their funds

## Recommendation
Please consider handling the edge case when transfers for the same transaction are split into indexer query windows
