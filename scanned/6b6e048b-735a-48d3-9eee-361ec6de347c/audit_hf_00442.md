# [H] Sol scan may be DoSed and locks

## Summary
Severity: High
Contest weight: 0.3766
Dataset id: 1864
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The bridge uses polling of solana signatures to the address of the bridge ms. Inside these signature objects, individual instructions are parsed and parameters for transfers are extracted. One of these parameters is the native fee to be paid to the bridge. Unfortunately if the fee is insufficient a panic is triggered in the bridge code. Due to the recovery of the go routine, the bridge will attempt to iterate on the failed signature until reaching window limit of 100 (polling window of the indexer), at which point some signatures will be skipped during high usage.
chain_sol.go#L66-L104:
```go
func (b *Bridge) solScanBurn(id, signer string, blockTime time.Time, decoder *SolanaDecoder, mint string) *Transfer {
    _ = decoder.String()
    amount := IntToBi(int64(decoder.Uint64()))
    fee := decoder.Uint64()
    targetNetwork := decoder.Uint8()
    targetAddress := decoder.String()
    if fee < 50000000 {
        panic(fmt.Sprintf("sol fee paid to small to cover transaction cost: %d", fee))
    }
    return &Transfer{
        ID: id,
        Target: int(targetNetwork),
        From: signer,
        To: targetAddress,
        Rune: mint,
        Amount: amount.String(),
        Created: blockTime,
    }
}

// parses a lock instruction details into a transfer
func (b *Bridge) solScanLock(id, signer string, blockTime time.Time, decoder *SolanaDecoder, mint string) *Transfer {
    amount := IntToBi(int64(decoder.Uint64()))
    fee := decoder.Uint64()
    targetNetwork := decoder.Uint8()
    targetAddress := decoder.String()
    if fee < 50000000 {
        panic(fmt.Sprintf("sol fee paid to small to cover transaction cost: %d", fee))
    }
    return &Transfer{
        ID: id,
        Target: int(targetNetwork),
        From: signer,
        To: targetAddress,
        Rune: mint,
        Amount: amount.String(),
        Created: blockTime,
    }
}
```
Internal pre-conditions
External pre-conditions
Attack Path
1. Malicious user locks small amount of tokens to solana bridge program and provides too small of a fee to be processed by the bridge
Some user events will be skipped with high probability, causing loss of locked funds for users

## Recommendation
Please consider recovering from these errors gracefully by saving the transfer with an error or ignored status
