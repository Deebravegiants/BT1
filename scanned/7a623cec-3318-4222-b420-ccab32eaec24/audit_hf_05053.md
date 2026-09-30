# [M] Treasury cap restriction will not

## Summary
Severity: Medium
Contest weight: 0.2649
Dataset id: 23058
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Treasury cap restriction will not hold and one block per month will be compromised
Once a month emissions are calculated and there is no cap checking before .AddEcosystemTokensMinted.
if blockEmission.GT(ecosystemBalance) {
// mint the amount of tokens required to pay out the emissions
tokensToMint := blockEmission.Sub(ecosystemBalance)
coins := sdk.NewCoins(sdk.NewCoin(params.MintDenom, tokensToMint))
err = k.MintCoins(sdkCtx, coins)
if err != nil {
return err
}
err = k.MoveCoinsFromMintToEcosystem(sdkCtx, coins)
if err != nil {
return err
}
// then increment the recorded history of the amount of tokens minted
if err != nil {
return err
}
}
x/mint/module/abci.go#L178 if minted is more than cap there would be negative number here
func GetEcosystemMintSupplyRemaining(
ctx sdk.Context,
k keeper.Keeper,
params types.Params,
) (math.Int, error) {
// calculate how many tokens left the ecosystem account is allowed to mint
ecosystemTokensAlreadyMinted, err := k.EcosystemTokensMinted.Get(ctx)
if err != nil {
return math.Int{}, err
}
// check that you are allowed to mint more tokens and we haven't hit the max supply
ecosystemMaxSupply := math.LegacyNewDecFromInt(params.MaxSupply).
Mul(params.EcosystemTreasuryPercentOfTotalSupply).TruncateInt()
return ecosystemMaxSupply.Sub(ecosystemTokensAlreadyMinted), nil
}
x/mint/module/abci.go#L89 Which will trigger error invocation here
ratioCirculating := circulatingSupply.ToLegacyDec().Quo(maxSupply.ToLegacyDec())
ratioEcosystemToStaked :=
ecosystemMintableRemaining.ToLegacyDec().Quo(networkStaked.ToLegacyDec())
ret := fEmission.
Mul(ratioEcosystemToStaked).
Mul(ratioCirculating)
if ret.IsNegative() {
return math.LegacyDec{}, errors.Wrapf(
types.ErrNegativeTargetEmissionPerToken,
"target emission per token is negative: %s | %s | %s",
ratioCirculating.String(),
ratioEcosystemToStaked.String(),
ret.String(),
)
}
return ret, nil
}
mint/keeper/emissions.go#L148 which will compromised block
Cap restriction will not hold and one block per month will be compromised

## Recommendation
if blockEmission.GT(ecosystemBalance) {
// mint the amount of tokens required to pay out the emissions
tokensToMint := blockEmission.Sub(ecosystemBalance)
+
if( tokensToMint > ecosystemMintSupplyRemaining ){
+
tokensToMint := ecosystemMintSupplyRemaining
+
}
coins := sdk.NewCoins(sdk.NewCoin(params.MintDenom, tokensToMint))
err = k.MintCoins(sdkCtx, coins)
if err != nil {
return err
}
err = k.MoveCoinsFromMintToEcosystem(sdkCtx, coins)
if err != nil {
return err
}
// then increment the recorded history of the amount of tokens minted
err = k.AddEcosystemTokensMinted(ctx, tokensToMint)
if err != nil {
return err
}
}
