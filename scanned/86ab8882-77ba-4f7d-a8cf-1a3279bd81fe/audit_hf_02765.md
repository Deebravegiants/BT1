# [M] Arithmetic Overflow In coin_selection()

## Summary
Severity: Medium
Contest weight: 0.1385
Dataset id: 15139
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the coin_selection() function, the value of each output in the transaction is subtracted by a fee. This ensures the transaction costs are covered by the peg-outs. However, no check is performed to ensure that the value of the output is larger than the fee. Hence, an overflow may occur on line [126]. For this case, the output will have an excessively high value which would result in the transaction being invalid due to insufficient balance.
The impact is a block in the peg-out mechanism which may result in a denial of service.
bin/btc-server/src/wallet/coin_selection.rs
```rust
for (output, _pegout_id) in pegouts.iter_mut() {
    output.value -= fee_per_output; // @audit potential overflow
}
```
Note there is some limitation in the Solidity contract burn() function, which sets a minimum balance of a peg-out. However, this value may not be sufficient when there are a large number of input UTXOs required to craft the transaction.

## Recommendation
It is recommended to implement logic for handling outputs with a small value.
