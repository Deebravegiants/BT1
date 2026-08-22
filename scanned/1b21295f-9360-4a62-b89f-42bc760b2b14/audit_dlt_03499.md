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

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/177_
