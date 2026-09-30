# [H] Possible Flooding Attacks in handleMsgOrderRetry()

## Summary
Severity: High
Contest weight: 0.3740
Dataset id: 12183
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As discussed in earlier sections, the transfer module handles 21 different message types. In this section, we focus on the handling logic of one particular message type, i.e., MsgOrderRetry. Its sole purpose is to retry orders in case previous tries do not finish. This message type has a field named RetryTimes. Our analysis shows that this field have not gone through rigorous checks. Because of that, it is possible to send a series of MsgOrderRetry messages with the same OrderIDs and from but with different RetryTimes. As a result, the handler proceeds the execution to a function called addOrderRetryConfirmNode (see the code snippet below), which keeps storing these conﬁrmed messages into local store. Notice that the store key is calculated via retryOrderKey(strings.Join(orderIDs, "&"), retrytimes). This indicates that key length can be arbitrarily controlled by user input, i.e., OrderIDs, and these occupied storage space will not be released forever. At the very least, it results in resource waste or inefﬁciency. When the accumulated waste occupies the full storage space, it eventually jeopardizes various normal chain-wide operations.
```go
func (keeper BaseKeeper) addOrderRetryConfirmNode(ctx sdk.Context, txID, validatorAddr string, retrytimes uint32, valsNum int) bool {
    retryOrderConfirmNodes := []string{}
    store := ctx.KVStore(keeper.storeKey)
    bz := store.Get(retryOrderKey(txID, retrytimes))
    if bz != nil {
        keeper.cdc.MustUnmarshalBinaryBare(bz, &retryOrderConfirmNodes)
    }
    bFind := false
    for _, v := range retryOrderConfirmNodes {
        if v == validatorAddr {
            bFind = true
            break
        }
    }
    if !bFind {
        retryOrderConfirmNodes = append(retryOrderConfirmNodes, validatorAddr)
        bz = keeper.cdc.MustMarshalBinaryBare(retryOrderConfirmNodes)
        store.Set(retryOrderKey(txID, retrytimes), bz)
    }
    // have been confirmed
    if len(retryOrderConfirmNodes) >= sdk.Majority23(valsNum) {
        return true
    }
    return false
}
```

## Recommendation
Apply additional checks on RetryTimes in MsgOrderRetry.
