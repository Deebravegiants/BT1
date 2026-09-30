# [?] fix(x/auth/tx): avoid nil pointer panic in GetSigningTxData (#26527)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2026-06-16
Source: https://github.com/cosmos/cosmos-sdk/commit/a6689ba21ca5272b4c2f9bf7b0c3735acff9b419
Type: security-commit

## Details
fix(x/auth/tx): avoid nil pointer panic in GetSigningTxData (#26527)

## Patch
### CHANGELOG.md
```diff
@@ -79,6 +79,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 * (x/staking) [#26483](https://github.com/cosmos/cosmos-sdk/pull/26483) Block `MsgCreateValidator` from creating validators with cons addrs locked by key rotations.
 * (blockstm) [#25893](https://github.com/cosmos/cosmos-sdk/pull/25893) Fix CancelAll cancellation by clearing blocker ESTIMATE marks before waking suspended executors.
 * (crypto) [#26529](https://github.com/cosmos/cosmos-sdk/pull/26529) Validate the SEC1 tag byte (`0x02`/`0x03`) when unmarshaling a `secp256k1.PubKey`, rejecting malformed compressed keys that previously passed the length-only check.
+* (x/auth/tx) [#26527](https://github.com/cosmos/cosmos-sdk/pull/26527) Fix nil pointer panic in `GetSigningTxData` when a `SignerInfo` has a nil `PublicKey`.
 
 ### Deprecated
 
```

### x/auth/tx/adapter.go
```diff
@@ -60,13 +60,19 @@ func (w *wrapper) GetSigningTxData() txsigning.TxData {
 		modeInfo := &txv1beta1.ModeInfo{}
 		adaptModeInfo(signerInfo.ModeInfo, modeInfo)
 		txSignerInfo := &txv1beta1.SignerInfo{
-			PublicKey: &anypb.Any{
-				TypeUrl: signerInfo.PublicKey.TypeUrl,
-				Value:   signerInfo.PublicKey.Value,
-			},
 			Sequence: signerInfo.Sequence,
 			ModeInfo: modeInfo,
 		}
+		// PublicKey may legitimately be nil in a SignerInfo (the key can be
+		// omitted when it is already known, e.g. for some multisig sub-signers),
+		// as GetPubKeys already tolerates. Only convert it when present to avoid
+		// a nil pointer dereference.
+		if signerInfo.PublicKey != nil {
+			txSignerInfo.PublicKey = &anypb.Any{
+				TypeUrl: signerInfo.PublicKey.TypeUrl,
+				Value:   signerInfo.PublicKey.Value,
+			}
+		}
 		txSignerInfos[i] = txSignerInfo
 	}
 
```

### x/auth/tx/builder_test.go
```diff
@@ -361,3 +361,41 @@ func TestBuilderWithTimeoutTimestamp(t *testing.T) {
 	b := txBldr.(*wrapper)
 	require.True(t, b.tx.Body.TimeoutTimestamp.Equal(timeoutTimestamp))
 }
+
+func TestGetSigningTxData_NilPublicKey(t *testing.T) {
+	marshaler := codec.NewProtoCodec(codectypes.NewInterfaceRegistry())
+	w := newBuilder(marshaler)
+
+	_, pubkey, addr := testdata.KeyTestPubAddr()
+	require.NoError(t, w.SetMsgs(testdata.NewTestMsg(addr)))
+
+	// One signer provides a public key, the other omits it. A nil PublicKey is
+	// valid (the key can be omitted when already known, e.g. for some multisig
+	// sub-signers), and GetPubKeys already tolerates it. GetSigningTxData must
+	// convert the present key faithfully and not panic on the nil one.
+	withKey := signing.SignatureV2{
+		PubKey:   pubkey,
+		Data:     &signing.SingleSignatureData{SignMode: signing.SignMode_SIGN_MODE_DIRECT},
+		Sequence: 0,
+	}
+	withoutKey := signing.SignatureV2{
+		PubKey:   nil,
+		Data:     &signing.SingleSignatureData{SignMode: signing.SignMode_SIGN_MODE_DIRECT},
+		Sequence: 1,
+	}
+	require.NoError(t, w.SetSignatures(withKey, withoutKey))
+
+	require.NotPanics(t, func() {
+		td := w.GetSigningTxData()
+		require.Len(t, td.AuthInfo.SignerInfos, 2)
+
+		// The present key is converted faithfully.
+		src := w.tx.AuthInfo.SignerInfos[0].PublicKey
+		require.NotNil(t, td.AuthInfo.SignerInfos[0].PublicKey)
+		require.Equal(t, src.TypeUrl, td.AuthInfo.SignerInfos[0].PublicKey.TypeUrl)
+		require.Equal(t, src.Value, td.AuthInfo.SignerInfos[0].PublicKey.Value)
+
+		// The omitted key stays nil instead of triggering a panic.
+		require.Nil(t, td.AuthInfo.SignerInfos[1].PublicKey)
+	})
+}
```
