# [M] `ZetaSupplyChecker` calculation error

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-05
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/177
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/zeta_supply_checker.go#L177-L191
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/zeta_supply_checker.go#L153-L155
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L157-L165


# Vulnerability details

## Impact
Due to the incorrect calculation of `AbortedTxAmount`, the result of `ZetaSupplyChecker` is erroneous.

## Proof of Concept
In `ZetaSupplyChecker`, to verify if the supply is correct, the following formula is used:
```
eth locked + aborted amount == zeta supply on node + zeta in transit + external supply + genesis amount
```

The calculation for the `aborted amount` is as follows:

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/zeta_supply_checker.go#L177-L191
```go
func (zs *ZetaSupplyChecker) AbortedTxAmount() (sdkmath.Int, error) {
	cctxList, err := zs.zetaClient.GetCctxByStatus(types.CctxStatus_Aborted)
	if err != nil {
		return sdkmath.ZeroInt(), err
	}
	amount := sdkmath.ZeroUint()
	for _, cctx := range cctxList {
		amount = amount.Add(cctx.GetCurrentOutTxParam().Amount)
	}
	amountInt, ok := sdkmath.NewIntFromString(amount.String())
	if !ok {
		return sdkmath.ZeroInt(), errors.New("error parsing amount")
	}
	return amountInt, nil
}
```

The problem arises here by directly taking `cctx.GetCurrentOutTxParam().Amount`, without determining whether the `coinType` of this `cctx` is ZETA.

When a revert cctx is created, `outParam.coinType` is set to `cctx.InboundTxParams.CoinType`, which can be gas or ERC20, and not necessarily ZETA.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L157-L165
```go
			// create new OutboundTxParams for the revert
			revertTxParams := &types.OutboundTxParams{
				Receiver:           cctx.InboundTxParams.Sender,
				ReceiverChainId:    cctx.InboundTxParams.SenderChainId,
				Amount:             cctx.InboundTxParams.Amount,
				CoinType:           cctx.InboundTxParams.CoinType,
				OutboundTxGasLimit: gasLimit,
			}
			cctx.OutboundTxParams = append(cctx.OutboundTxParams, revertTxParams)
```

If the revert `cctx` fails and turns into `aborted`, for example, in the following code snippet, then this non-ZETA `amount` will be recorded in `AbortedTxAmount`.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L191-L203
```go
				if cctx.InboundTxParams.CoinType == common.CoinType_ERC20 {

					if err := k.RefundAmountOnZetaChain(ctx, cctx, cctx.InboundTxParams.Amount); err != nil {
						// log the error
						k.Logger(ctx).Error("failed to refund amount of aborted cctx on ZetaChain",
							"error", err,
							"sender", cctx.InboundTxParams.Sender,
							"amount", cctx.InboundTxParams.Amount.String(),
						)
					}
				}

				cctx.CctxStatus.ChangeStatus(types.CctxStatus_Aborted, err.Error())
```

Therefore, the quantity returned by `AbortedTxAmount` is greater than the actual amount of ZETA.

## Tools Used
vscode
## Recommended Mitigation Steps
Ensure `coinType` is ZETA before recording the `amount`.





## Assessed type

Invalid Validation
