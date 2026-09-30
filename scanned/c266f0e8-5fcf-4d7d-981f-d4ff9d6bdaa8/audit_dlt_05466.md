# [?] Fix gov proposal end-of-voting-period consensus failure. (#1103)

## Summary
Severity: Unknown
Chain: Provenance
Component: provenance-io/provenance
Published: 2022-09-29
Source: https://github.com/provenance-io/provenance/commit/8806c0f17c13b94f5cb2f0f3a0cde53dc1607624
Type: security-commit

## Details
Fix gov proposal end-of-voting-period consensus failure. (#1103)

* [1099]: Add the types to the error messages when it's not a fee tx or not a fee gas meter.

* [1099]: bypass the consumeMsgFees stuff in the message service router if the gas meter isn't a fee gas meter.

## Patch
### internal/antewrapper/ante.go
```diff
@@ -30,7 +30,7 @@ func (r FeeMeterContextDecorator) AnteHandle(ctx sdk.Context, tx sdk.Tx, simulat
 func GetFeeTx(tx sdk.Tx) (sdk.FeeTx, error) {
 	feeTx, ok := tx.(sdk.FeeTx)
 	if !ok {
-		return nil, sdkerrors.ErrTxDecode.Wrap("Tx must be a FeeTx")
+		return nil, sdkerrors.ErrTxDecode.Wrapf("Tx must be a FeeTx: %T", tx)
 	}
 	return feeTx, nil
 }
@@ -39,7 +39,7 @@ func GetFeeTx(tx sdk.Tx) (sdk.FeeTx, error) {
 func GetFeeGasMeter(ctx sdk.Context) (*FeeGasMeter, error) {
 	feeGasMeter, ok := ctx.GasMeter().(*FeeGasMeter)
 	if !ok {
-		return nil, sdkerrors.ErrLogic.Wrap("gas meter is not a FeeGasMeter")
+		return nil, sdkerrors.ErrLogic.Wrapf("gas meter is not a FeeGasMeter: %T", ctx.GasMeter())
 	}
 	return feeGasMeter, nil
 }
```

### internal/handlers/msg_service_router.go
```diff
@@ -165,7 +165,11 @@ func noopInterceptor(_ context.Context, _ interface{}, _ *grpc.UnaryServerInfo,
 func (msr *PioMsgServiceRouter) consumeMsgFees(ctx sdk.Context, req sdk.Msg) error {
 	feeGasMeter, err := antewrapper.GetFeeGasMeter(ctx)
 	if err != nil {
-		panic(err)
+		// The x/gov module calls the message service router for proposal messages that have passed.
+		// In such cases, the antehandler is not run, so the gas meter will not be a fee gas meter.
+		// But those messages were voted on and have passed, so they should be processed regardless of msg fees.
+		// So in here, if there's an error getting the fee gas meter, we skip all this msg fee consumption.
+		return nil
 	}
 
 	tx, err := msr.decoder(ctx.TxBytes())
```
