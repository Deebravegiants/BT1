# [?] fix(x/auth/tx): avoid nil pointer panic in GetSigningTxData for multisig ModeInfo with a nil Multi or nil Bitarray (#26571)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2026-07-13
Source: https://github.com/cosmos/cosmos-sdk/commit/3a2772b3f326e57426fea07a9b36e67a056c9b67
Type: security-commit

## Details
fix(x/auth/tx): avoid nil pointer panic in GetSigningTxData for multisig ModeInfo with a nil Multi or nil Bitarray (#26571)

## Patch
### CHANGELOG.md
```diff
@@ -82,6 +82,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 * (x/staking) [#26483](https://github.com/cosmos/cosmos-sdk/pull/26483) Block `MsgCreateValidator` from creating validators with cons addrs locked by key rotations.
 * (blockstm) [#25893](https://github.com/cosmos/cosmos-sdk/pull/25893) Fix CancelAll cancellation by clearing blocker ESTIMATE marks before waking suspended executors.
 * (crypto) [#26529](https://github.com/cosmos/cosmos-sdk/pull/26529) Validate the SEC1 tag byte (`0x02`/`0x03`) when unmarshaling a `secp256k1.PubKey`, rejecting malformed compressed keys that previously passed the length-only check.
+* (x/auth/tx) [#26571](https://github.com/cosmos/cosmos-sdk/pull/26571) Avoid nil pointer panic in `GetSigningTxData` for multisig `ModeInfo` with a nil `Multi` or nil `Bitarray`.
 * (x/auth/tx) [#26527](https://github.com/cosmos/cosmos-sdk/pull/26527) Fix nil pointer panic in `GetSigningTxData` when a `SignerInfo` has a nil `PublicKey`.
 * (x/auth/tx) [#26517](https://github.com/cosmos/cosmos-sdk/pull/26517) Return a decode error instead of panicking when a transaction's `SignerInfos` and `Signatures` counts disagree in `GetSignaturesV2`, or a multisig's `ModeInfos` and sub-signature counts disagree in `ModeInfoAndSigToSignatureData`.
 * (x/auth/ante) [#26573](https://github.com/cosmos/cosmos-sdk/pull/26573) Reject tx with extra SignerInfos in SetPubKeyDecorator.
```

### x/auth/tx/adapter.go
```diff
@@ -129,17 +129,25 @@ func adaptModeInfo(legacy *tx.ModeInfo, res *txv1beta1.ModeInfo) {
 			},
 		}
 	case *tx.ModeInfo_Multi_:
-		multiModeInfos := legacy.GetMulti().ModeInfos
+		if mi.Multi == nil {
+			res.Sum = &txv1beta1.ModeInfo_Multi_{Multi: &txv1beta1.ModeInfo_Multi{}}
+			return
+		}
+		multiModeInfos := mi.Multi.ModeInfos
 		modeInfos := make([]*txv1beta1.ModeInfo, len(multiModeInfos))
 		for _, modeInfo := range multiModeInfos {
 			adaptModeInfo(modeInfo, &txv1beta1.ModeInfo{})
 		}
+		var bitarray *multisigv1beta1.CompactBitArray
+		if mi.Multi.Bitarray != nil {
+			bitarray = &multisigv1beta1.CompactBitArray{
+				Elems:           mi.Multi.Bitarray.Elems,
+				ExtraBitsStored: mi.Multi.Bitarray.ExtraBitsStored,
+			}
+		}
 		res.Sum = &txv1beta1.ModeInfo_Multi_{
 			Multi: &txv1beta1.ModeInfo_Multi{
-				Bitarray: &multisigv1beta1.CompactBitArray{
-					Elems:           mi.Multi.Bitarray.Elems,
-					ExtraBitsStored: mi.Multi.Bitarray.ExtraBitsStored,
-				},
+				Bitarray:  bitarray,
 				ModeInfos: modeInfos,
 			},
 		}
```

### x/auth/tx/builder_test.go
```diff
@@ -399,3 +399,56 @@ func TestGetSigningTxData_NilPublicKey(t *testing.T) {
 		require.Nil(t, td.AuthInfo.SignerInfos[1].PublicKey)
 	})
 }
+
+func TestGetSigningTxData_NilMultiBitarray(t *testing.T) {
+	marshaler := codec.NewProtoCodec(codectypes.NewInterfaceRegistry())
+	w := newBuilder(marshaler)
+
+	_, _, addr := testdata.KeyTestPubAddr()
+	require.NoError(t, w.SetMsgs(testdata.NewTestMsg(addr)))
+
+	// Inject a SignerInfo with ModeInfo_Multi whose Bitarray is nil — valid
+	// wire state that survives decoding if the field is omitted. Before the
+	// fix, adaptModeInfo would dereference nil and panic.
+	w.tx.AuthInfo.SignerInfos = []*txtypes.SignerInfo{
+		{
+			ModeInfo: &txtypes.ModeInfo{
+				Sum: &txtypes.ModeInfo_Multi_{
+					Multi: &txtypes.ModeInfo_Multi{
+						Bitarray: nil,
+					},
+				},
+			},
+		},
+	}
+
+	require.NotPanics(t, func() {
+		td := w.GetSigningTxData()
+		require.Len(t, td.AuthInfo.SignerInfos, 1)
+		require.Nil(t, td.AuthInfo.SignerInfos[0].ModeInfo.GetMulti().Bitarray)
+	})
+}
+
+func TestGetSigningTxData_NilModeInfoMulti(t *testing.T) {
+	marshaler := codec.NewProtoCodec(codectypes.NewInterfaceRegistry())
+	w := newBuilder(marshaler)
+
+	_, _, addr := testdata.KeyTestPubAddr()
+	require.NoError(t, w.SetMsgs(testdata.NewTestMsg(addr)))
+
+	w.tx.AuthInfo.SignerInfos = []*txtypes.SignerInfo{
+		{
+			ModeInfo: &txtypes.ModeInfo{
+				Sum: &txtypes.ModeInfo_Multi_{
+					Multi: nil,
+				},
+			},
+		},
+	}
+
+	require.NotPanics(t, func() {
+		td := w.GetSigningTxData()
+		require.Len(t, td.AuthInfo.SignerInfos, 1)
+		require.NotNil(t, td.AuthInfo.SignerInfos[0].ModeInfo.GetMulti())
+	})
+}
```
