# [M] LES (Light Ethereum Subprotocol) doesn't for-

## Summary
Severity: Medium
Contest weight: 0.1866
Dataset id: 19735
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LES (Light Ethereum Subprotocol) doesn't forward the transaction to the sequencer when receiving it over RPC.
When a user submits a transaction to op-geth node (validator/verifier mode), the node sends the transaction to the sequencer, if no error, it adds it to the tx pool.
func (b *EthAPIBackend) SendTx(ctx context.Context, tx *types.Transaction) error {
    if b.eth.seqRPCService != nil {
        data, err := tx.MarshalBinary()
        if err != nil {
            return err
        }
        if err := b.eth.seqRPCService.CallContext(ctx, nil, "eth_sendRawTransaction", hexutil.Encode(data)); err != nil {
            return err
        }
    }
    return b.eth.txPool.AddLocal(tx)
}
https://github.com/ethereum-optimism/op-geth/blob/optimism-history/eth/api_backend.go#L253-L264
However, when LES, it only adds the transaction to the tx pool.
func (b *LesApiBackend) SendTx(ctx context.Context, signedTx *types.Transaction) error {
    return b.eth.txPool.Add(ctx, signedTx)
}
https://github.com/ethereum-optimism/op-geth/blob/optimism-history/les/api_backend.go#L193-L195
• Transaction isn't sent to the sequencer and will never be processed (submitted to L1).
• Inconsistency among op-geth nodes validators/verifiers and the sequencer.
• Additionally, from UX perspective, it is misleading as the user would think the transaction was submitted "successfully".

## Recommendation
Match this RPC change in the LES RPC. As it seems to be overlooked.
Ref: https://op-geth.optimism.io/
