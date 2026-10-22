# [M] Unrecognized Contract-Sourced ETH Deposits in Chainnode

## Summary
Severity: Medium
Contest weight: 0.2466
Dataset id: 12185
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
HBTC Chain has a chainnode component that actively listens to (and synchronizes with) external chains such as BTC and Ethereum. This component is important in timely recognizing user deposits that eventually kick off subsequent collection operations. We show below the code snippet that is part of Ethereum adaptor. In particular, it builds a response with incoming deposits of both ETH and other ERC-20 assets. Notice that ETH deposits are recognized only for transaction destination (toAddress.String()) at the outer layer. In other words, other deposits from internal transactions are ignored and thus not accepted. The deposits of ERC-20 assets are properly recognized by following the standard ERC-20 Transfer event specification, regardless of internal-transaction deposits or straightforward EOA deposits. As a result, current implementation may miss ETH deposits from internal transactions. Considering the growing popularity of smart wallets in cooperation with various DeFi protocols, it may need to be revisited to accommodate ETH deposits from these smart wallets (and these deposits are part of internal transactions).
```go
costFee := new(big.Int).Mul(new(big.Int).SetUint64(receipt.GasUsed), tx.GasPrice())
if tx.Value().Cmp(big.NewInt(0)) == 1 {
    replyCh <- &proto.QueryAccountTransactionReply{
        TxHash: tx.Hash().String(),
        TxStatus: proto.TxStatus_Success,
        From: sender.String(),
        To: toAddress.String(),
        Amount: tx.Value().String(),
        Memo: "",
        Nonce: tx.Nonce(),
        GasLimit: new(big.Int).SetUint64(tx.Gas()).String(),
        GasPrice: tx.GasPrice().String(),
        CostFee: costFee.String(),
        BlockHeight: uint64(height),
        BlockTime: block.Time(),
        SignHash: signer.Hash(tx).Bytes(),
        ContractAddress: "",
    }
}
for _, receiptLog := range receipt.Logs {
    if receiptLog.Removed {
        continue
    }
    if len(receiptLog.Topics) != 3 {
        continue
    }
    if receiptLog.Topics[0] != common.HexToHash("0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef") {
        continue
    }
    tokenFromAddress := common.BytesToAddress(receiptLog.Topics[1].Bytes())
    tokenToAddress := common.BytesToAddress(receiptLog.Topics[2].Bytes())
    tokenAmount, ok := big.NewInt(0).SetString(fmt.Sprintf("%x", receiptLog.Data), 16)
    if !ok {
        errCh <- errors.New("failed to decode token amount from receipt log data")
        needStop.Store(true)
        return
    }
    if tokenAmount.Cmp(big.NewInt(0)) == 1 {
        replyCh <- &proto.QueryAccountTransactionReply{
            TxHash: tx.Hash().String(),
            TxStatus: proto.TxStatus_Success,
            From: tokenFromAddress.String(),
            To: tokenToAddress.String(),
            Amount: tokenAmount.String(),
            Memo: "",
            Nonce: tx.Nonce(),
            GasLimit: new(big.Int).SetUint64(tx.Gas()).String(),
            GasPrice: tx.GasPrice().String(),
            CostFee: costFee.String(),
            BlockHeight: uint64(height),
            BlockTime: block.Time(),
            SignHash: signer.Hash(tx).Bytes(),
            ContractAddress: receiptLog.Address.String(),
        }
    }
}
```
to perform balance difference check between current blockheight and the previous one (i.e., with blockheight-1). Any inconsistency warrants a manual follow-up for unambiguous resolution.

## Recommendation
For better DeFi adoption, it is recommended to accept deposits of ETH assets sourced from smart contracts.
