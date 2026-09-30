# [M] Improper Fee Return in handleMsgKeyGenFinish()

## Summary
Severity: Medium
Contest weight: 0.5842
Dataset id: 12192
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As described in Section 3.1, the keygen module provides dynamic key generation services for cross-chain assets. Speciﬁcally, it has a few handlers to process various types of messages. In the previous sections, we have been focusing on the handleMsgKeyGen() handler that processes MsgKeyGen messages. In this section, we examine another handler, i.e., handleMsgKeyGenFinish(), which processes MsgKeyGenFinish messages.
As the name indicates, these messages notify the HBTC Chain that previous requests for key generation have been ﬁnished.
There is an issue inside handleMsgKeyGenFinish() that improperly returns back the opening fee back to the requesting users. Moreover, it further disseminates the same amount of opening fee to the distr module, resulting in an unintended inﬂation on hbc - the HBTC Chain native token.
Speciﬁcally, we show below the related code snippet inside the handleMsgKeyGenFinish() handler. After performing necessary sanity checks on the MsgKeyGenFinish message, the system eventu-ally charges the opening fee by moving the amount of opening fee (previously on hold on fromCU.SubCoinsHold) to distr. However, the line 305 indicates that the opening fee is also returned back to fromCU.
```solidity
...
// sub openfee
fromCU := keeper.ck.GetCU(ctx, fromCUAddr)
openFee := keyGenOrder.OpenFee
hasFee := openFee.IsAllGT(sdk.NewCoins(sdk.NewCoin(sdk.NativeToken, sdk.ZeroInt())))
if hasFee
Public
    fromCU.SubCoinsHold(openFee)
    fromCU.AddCoins(openFee)
    keeper.ck.SetCU(ctx, fromCU)
    keeper.dk.AddToFeePool(ctx, sdk.NewDecCoins(openFee))
...
```

## Recommendation
There is no need to return back the key-generation opening fee back to the requesting fromCU.
```solidity
...
// sub openfee
fromCU := keeper.ck.GetCU(ctx, fromCUAddr)
openFee := keyGenOrder.OpenFee
hasFee := openFee.IsAllGT(sdk.NewCoins(sdk.NewCoin(sdk.NativeToken, sdk.ZeroInt())))
if hasFee {
    fromCU.SubCoinsHold(openFee)
    // fromCU.AddCoins(openFee)
    keeper.ck.SetCU(ctx, fromCU)
    keeper.dk.AddToFeePool(ctx, sdk.NewDecCoins(openFee))
}
...
```
