# [H] Unintended Deposit Removal in OpcuAssetTransfer()

## Summary
Severity: High
Contest weight: 0.7856
Dataset id: 12194
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the transfer module is one of the most crucial modules and its main functionality is to allow for asset transfers inside and outside HBTC Chain. In the last section, we have examined a vulnerability related to MsgOpcuAssetTransfer handling. In this section, we examine another issue within the same handler that could lead to unintended removal of legitimate deposits. Specifically, this OpcuAssetTransfer handler takes a few arguments that specify the related Opcu account opCUAddr, the new destination address toAddr, the asset symbol symbol, as well as related Public TransferItems included in this particular transfer. To facilitate the organization and management of the entire transfer process, HBTC Chain has its internal order system. And each particular transfer has its unique orderID. Different transfers will have different orderIDs.

The last issue deals with the non-freshness of one argument toAddr. This issue is related to duplicability in another argument TransferItems. We show below the message type MsgOpcuAssetTransfer's validity check routine: ValidateBasic(). Apparently, there is a check on TransferItems. But it only ensures that the TransferItems array is not empty. In other words, it does not check whether any item in the array is duplicated or not. As a result, we can construct a message type with duplicates in TransferItems.
```solidity
// quick validity check
func (msg MsgOpcuAssetTransfer) ValidateBasic() sdk.Error {
    // note that unmarshaling from bech32 ensures either empty or valid
    err := sdk.CUAddressFromBase58(msg.FromCU)
    if err != nil {
        return ErrBadAddress(DefaultCodespace)
    }
    err = sdk.CUAddressFromBase58(msg.OpCU)
    if err != nil {
        return ErrBadAddress(DefaultCodespace)
    }
    if msg.ToAddr == "" {
        return ErrBadAddress(DefaultCodespace)
    }
    if msg.OrderID == "" {
        return ErrNilOrderID(DefaultCodespace)
    }
    if len(msg.TransferItems) == 0 {
        return sdk.ErrInvalidTx("transfer items are empty")
    }
    return nil
}
```
. (If there is none, we can always create one.) In the meantime, there is another TransferItem 퐵 with amount above OpcuAstTransferThreshold. For simplicity, A.amount=0.1*OpcuAstTransferThreshold, and B.amount=1.1*OpcuAstTransferThreshold. Accordingly, we can construct an array with two 퐴s and one 퐵 such that the sum of them meets the conditional check in line 98, i.e., sum.LTE(keeper.utxoOpcuAstTransferThreshold(len(items), tokenInfo)). Note that the right-end value grows linearly with the number of items in TransferItems, which implies it is always feasible to construct such Public TransferItems.
```solidity
sum := sdk.ZeroInt()
for _, item := range items {
    depositItem := keeper.ck.GetDeposit(ctx, symbol, opCUAddr, item.Hash, item.Index)
    if depositItem == sdk.DepositNil || !depositItem.Amount.Equal(item.Amount) || depositItem.Status == sdk.DepositItemStatusInProcess {
        return sdk.ErrInvalidTx(fmt.Sprintf("Invalid DepositItem (%v)", item.Hash)).Result()
    }
    sum = sum.Add(item.Amount)
}
if sum.LTE(keeper.utxoOpcuAstTransferThreshold(len(items), tokenInfo)) {
    for _, item := range items {
        keeper.ck.DelDeposit(ctx, symbol, opCUAddr, item.Hash, item.Index)
    }
    burnedCoins := sdk.NewCoins(sdk.NewCoin(symbol, sum))
    opCU.AddGasUsed(burnedCoins)
    keeper.ck.SetCU(ctx, opCU)
    if keeper.checkUtxoOpcuAstTransferFinish(ctx, fromAddr, symbol, opCU) {
        opCU.SetMigrationStatus(sdk.MigrationFinish)
        keeper.ck.SetCU(ctx, opCU)
        keeper.checkOpcusMigrationStatus(ctx, curEpoch)
    }
    return sdk.Result{}
}
```
is then safely deleted, causing possible loss on assets under opcu custody. In addition, it also messes up the internal GasUsed states.

## Recommendation
Add additional sanity checks to ensure the uniqueness of TransferItems. Public
