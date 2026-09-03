# [H] EL-2026-14: RLP decoding of transactions allows trailing bytes

## Summary
Severity: High
Chain: Ethereum (execution layer)
Component: Erigon
Source: https://notes.ethereum.org/5p5uV89yTXOincAhd3vARQ
Type: ef-disclosure

## Details
Short description *
1 sentence description of the bug
Erigon Consensus Bug - RLP Decoding of Transactions in Execution Payloads Allow Trailing Bytes
Attack scenario *
More detailed description of the attack/bug scenario and unexpected/buggy behaviour
The issue occurs within the processing of `eth_newPayloadV3` (and earlier versions) functions. Transactions are received from the Consensus Layer as raw bytes within the ExecutionPayload. These raw bytes are decode by the Execution Layer into typed transactions.

The bug within Erigon is that it allows trailing bytes to be appended to the RLP encoded transactions. These trailing bytes are rejected by other clients but accepted by Erigon.
The result is a consensus bug.

Note the yellow paper states trailing bytes are not allowed on page 8 section 6. Transaction Execution thus the bug is within Erigon and not other clients.
Impact *
 Describe the effect this may have in a production setting
If a block with a malicious transaction is shared from the CL client in `eth_newPayloadV3()` it will be accepted by Erigon as valid and added to the chain but rejected by other clients.
The result is a consensus split where Eirgon could have a different canonical head to the other clients.

Note that Erigon is not currently a majority client (~7% of nodes) and therefore consensus will eventually reorg the malicious block due to receiving insufficient attestations from nodes using other execution clients.
Components *
Point to the files, functions, and/or specific line numbers where the bug occurs
Engine API newPayload() - https://github.com/ledgerwatch/erigon/blob/v2.59.3/turbo/engineapi/engine_server.go#L200-L217  AND  UnmarshalTransactionFromBinary() - https://github.com/ledgerwatch/erigon/blob/v2.59.3/core/types/transaction.go#L170-L211
Reproduction *
If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.
The following test case can be added to `transaction_test.go` - https://github.com/ledgerwatch/erigon/blob/v2.59.3/core/types/transaction_test.go
```go
func TestTrailingBytes(t *testing.T) {
	// Create a valid transaction
	valid_rlp_transaction := []byte{201, 38, 38, 128, 128, 107, 58, 42, 38, 42}

	// Test valid transaction
	transactions := make([][]byte, 1)
	transactions[0] = valid_rlp_transaction

	for _, txn := range transactions {
		if TypedTransactionMarshalledAsRlpString(txn) {
			panic("TypedTransactionMarshalledAsRlpString() error")
		}
	}

```

_Trimmed to 38 lines — full report: https://notes.ethereum.org/5p5uV89yTXOincAhd3vARQ_
