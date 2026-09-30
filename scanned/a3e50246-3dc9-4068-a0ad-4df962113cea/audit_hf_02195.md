# [H] Asset Lockdown in OpcuAssetTransfer()

## Summary
Severity: High
Contest weight: 0.7863
Dataset id: 12193
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Among all modules in HBTC Chain, the transfer module is one of the most crucial modules and its main functionality is to actually transfer assets inside and outside HBTC Chain. Its complexity is also partially reﬂected in the number of messages it recognizes and handles. In total, there are 21 diﬀerent types of messages, including MsgSend, MsgDeposit, MsgWithdraw, MsgSysTransfer, MsgOpcuAssetTransfer, and their variants.
In this section, we mainly focus on the four speciﬁc message types related to opcu asset transfers: i.e., MsgOpcuAssetTransfer, MsgOpcuAssetTransferWaitSign, MsgOpcuAssetTransferSignFinish, and MsgOpcuAssetTransferFinish. Among these four message types, the ﬁrst one MsgOpcuAssetTransfer aims to kick oﬀ the process for transferring assets under opcu custody; the second one MsgOpcuAssetTransferWaitSign is responsible for starting the key-signing process on behalf of opcu and the keys are shared among active validators of HBTC Chain; the third one MsgOpcuAssetTransferSignFinish signals the accomplishment of key-signing process so that the signed transaction can be broadcasted and mined on chain; and the fourth one MsgOpcuAssetTransferFinish reaches the consensus in successfully completing the transfer transaction and therefore properly settles down necessary asset updates after the transfer.
If we delve into the MsgOpcuAssetTransfer-handling logic, this speciﬁc handler OpcuAssetTransfer takes a few arguments that specify the related opcu account opCUAddr, the new destination address toAddr, the asset symbol symbol, as well as related TransferItems included in this particular transfer. To facilitate the organization and management of the entire transfer process, HBTC Chain has its internal order system. And each particular transfer has its unique orderID. Diﬀerent transfers will have diﬀerent orderIDs.
However, this particular handler suﬀers from an issue that may be abused to lock down the funds being transferred. Speciﬁcally, it does NOT validate the freshness of the given destination address toAddr to ensure it is generated for current migration epoch. As a result, an outdated toAddr can be provided to bypass the following check (line 60).
```solidity
...
valid, canonicalToAddr := keeper.cn.ValidAddress(chain, symbol, toAddr)
if !valid {
    return sdk.ErrInvalidAddr(fmt.Sprintf("%v is not a valid address", toAddr)).Result()
}
toAsset := opCU.GetAssetByAddr(symbol, canonicalToAddr)
if toAsset == sdk.NilAsset {
    return sdk.ErrInvalidAddr(fmt.Sprintf("%v does not belong to cu %v", canonicalToAddr, opCU.GetAddress().String())).Result()
}
...
```
ﬁrst type relates to assets in BTC and the second type is about assets in Ethereum. For the BTC assets, each TransferItem will be accordingly marked as DepositItemStatusInProcess. As a result, the asset may not be released until the transfer process completes. For Ethereum assets, the opcu account will be marked as opCU.SetEnableSendTx(false, chain, fromAddr), which prevents any asset from being transferred under its custody unless the ﬂag is turned back to true.
```solidity
...
for _, item := range items {
    depositItem := keeper.ck.GetDeposit(ctx, symbol, opCUAddr, item.Hash, item.Index)
    if depositItem == sdk.DepositNil || !depositItem.Amount.Equal(item.Amount) || depositItem.Status == sdk.DepositItemStatusInProcess {
        return sdk.ErrInvalidTx(fmt.Sprintf("Invalid DepositItem (%v)", item.Hash)).Result()
    }
    sum = sum.Add(item.Amount)
}
...
for _, item := range items {
    keeper.ck.SetDepositStatus(ctx, symbol, opCUAddr, item.Hash, item.Index, sdk.DepositItemStatusInProcess)
}
...
```
old toAddr, which no one further holds the secret shares. If the transfer process does not complete, the internal states have been modiﬁed in a way that prevents the same TransferItems from being re-used or opCU from being transferable for assets under its custody. In either way, the funds are locked from future use.

## Recommendation
Add additional sanity checks to ensure the freshness of toAddr, i.e. it is the latest one being generated for current epoch.
