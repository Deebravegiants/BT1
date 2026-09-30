# [M] Missing Error Handling in SignedTx Veriﬁcation

## Summary
Severity: Medium
Contest weight: 0.2449
Dataset id: 12184
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Though the transfer module recognizes and processes 21 different types of messages, these messages typically revolves the business logic for user deposits, withdrawals, internal collection, opcu asset transfers, as well as gas fee transfer (for Account-based token types only). And the internal processing logic typically follows four different stages: Begin, WaitSign, SignFinish, and Finish. The first one indicates the intention to get started; the second one calls for the key-signing process and requires the responses from current validators; the third one ﬁnishes the key-signing process so that the signed transaction can be broadcasted and mined on chain; and the fourth one reaches the consensus in successfully completing the logic and therefore properly settles down necessary asset updates. In this section, we examine a common routine, i.e., verifyAccountBasedSignedTx, often used in the third stage that verifies the key signature from current validators. This routine is important and required to block any malicious attempt to corrupt the key signing behavior. However, within the routine (see the code snippet below), it misses an error handling (line 112). We point out that the return value from calling the chainnode.QueryAccountTransactionFromData(chain, symbol, rawData) takes the untrusted input rawdata and should be thoroughly validated. In the case when the returned value rawTx could be nil, the immediate access after the return will lead to a null pointer deference and crash the running process.
```go
func (keeper BaseKeeper) verifyAccountBasedSignedTx(fromAddr, chain, symbol string, rawData, signedTx []byte) (sdk.Result, string) {
    txHash := ""
    verified, err := keeper.cn.VerifyAccountSignedTransaction(chain, symbol, fromAddr, signedTx)
    if err != nil || !verified {
        return sdk.ErrInvalidTx(fmt.Sprintf("VerifyAccountSignedTransaction fail :%v, err :%v", signedTx, err)).Result(), txHash
    }
    tx, err := keeper.cn.QueryAccountTransactionFromSignedData(chain, symbol, signedTx)
    if err != nil {
        return sdk.ErrInvalidTx(fmt.Sprintf("QueryUtxoTransactionFromSignedData Error :%v", signedTx)).Result(), txHash
    }
    if tx.From != fromAddr {
        return sdk.ErrInvalidTx(fmt.Sprintf("from an unexpected address :%v, expected address :%v", tx.From, fromAddr)).Result(), txHash
    }
    rawTx, _, err := keeper.cn.QueryAccountTransactionFromData(chain, symbol, rawData)
    if err != nil {
        return sdk.ErrInvalidTx(fmt.Sprintf("QueryAccountTransactionFromData Error :%v", rawData)).Result(), txHash
    }
    if tx.To != rawTx.To {
        return sdk.ErrInvalidTx(fmt.Sprintf("to an unexpected address :%v, expected address :%v", tx.To, rawTx.To)).Result(), txHash
    }
    if !tx.Amount.Equal(rawTx.Amount) {
        return sdk.ErrInvalidTx(fmt.Sprintf("amount mismatch, expected :%v, actual :%v", rawTx.Amount, tx.Amount)).Result(), txHash
    }
    if !tx.GasPrice.Equal(rawTx.GasPrice) {
        return sdk.ErrInvalidTx(fmt.Sprintf("gasPrice mismatch, expected :%v, actual :%v", rawTx.GasPrice, tx.GasPrice)).Result(), txHash
    }
    if !tx.GasLimit.Equal(rawTx.GasLimit) {
        return sdk.ErrInvalidTx(fmt.Sprintf("gasLimit mismatch, expected :%v, actual :%v", rawTx.GasLimit, tx.GasLimit)).Result(), txHash
    }
    txHash = tx.Hash
    return sdk.Result{}, txHash
}
```

## Recommendation
Add necessary error handling in verifyAccountBasedSignedTx.
