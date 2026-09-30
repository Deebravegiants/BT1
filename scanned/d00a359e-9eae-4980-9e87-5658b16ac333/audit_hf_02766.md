# [C] Not All State Changes Are Reverted For An Invalid Peg-In Proof

## Summary
Severity: Critical
Contest weight: 0.2694
Dataset id: 15143
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A security vulnerability exists where an invalid proof may lead to a permanently adjusted peginBitcoinBlockHeight in the core node state.
If a peg-in proof is deemed invalid after a mint() operation, the receivers balance is decremented to its original value. However, the receiver's peginBitcoinBlockHeight is not reverted. Therefore, any user can change peginBitcoinBlockHeight for any receiver without needing a valid peg-in proof. As such, an attacker may increment peginBitcoinBlockHeight to u32::MAX for any receiver. Any subsequent calls to mint() will revert for that receiver. This may be used to frontrun any incoming mints and permanently freeze their bridged BTC.
Furthermore, the relayer's balance, that is the refundAddress in mint(), is also not reverted correctly after an invalid proof is sent. This means that a relayer has their transaction costs refunded even though the proof was not valid.
An attacker may abuse this with invalid calls to mint(), which fill up the block's gas limit since the transactions are effectively free.
The impact is rated as high as it will permanently prevent valid calls to mint() and will result in refunds being paid arbitrarily to addresses.

## Recommendation
Revert all state changes that occur in the call to mint() if the peg-in proof is deemed invalid.
