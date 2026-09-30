# [M] Free Key Generation in handleMsgKeyGen()

## Summary
Severity: Medium
Contest weight: 0.4479
Dataset id: 12191
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Among all modules in HBTC Chain, the keygen module is an important one. This particular module provides dynamic key generation services for cross-chain assets. Speciﬁcally, when a user requests for the creation of a custody address in a supported external chain (via a MsgKeyGen message), keygen processes the request in the handleMsgKeyGen handler by essentially delegating the request to the settle daemon.
Importantly, this module processes MsgKeyGen messages via the handleMsgKeyGen handler, which diﬀerentiates three types of scenarios: subToken, WaitAssignKeyGenOrder, and KeyGenOrder. The ﬁrst subToken scenario indicates the request for an address of an ERC20-like asset. The second WaitAssignKeyGenOrder scenario examines the presence of a pre-generated address and, if any, directly allocates one to answer the request. The third KeyGenOrder scenario leaves the heavy-lifting task of custody address key generation to settle.
The second scenario shares an issue that allows for free key generation. Speciﬁcally, the associated opening fee feeCoins has not been deducted from the requesting user fromCU, though the same amount has been credited to CommunityPool (via the keeper.dk.AddToFeePool() in line 158 in the following code snippet).
```solidity
...
flows := make([]sdk.Flow, 0, 3+len(keygenOrder.KeyNodes))
orderflow := keeper.rk.NewOrderFlow(symbol, fromAddr, orderID, sdk.OrderTypeKeyGen, sdk.OrderStatusFinish)
keyGenFinishFlow := sdk.KeyGenFinishFlow{OrderID: orderID, IsPreKeyGen: true, toAddr}
flows = append(flows, orderflow, keyGenFinishFlow)
Public
if feeCoins.IsAllGT(sdk.NewCoins(sdk.NewCoin(sdk.NativeToken, sdk.ZeroInt()))) {
    keeper.dk.AddToFeePool(ctx, sdk.NewDecCoins(feeCoins))
}
...
```

## Recommendation
The ﬁxup is straightforward as we need to properly charge the key-generation opening fee from the requesting fromCU onto the storage in second scenario: WaitAssignKeyGenOrder.
