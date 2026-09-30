# [?] lnwire: fix test data race

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-06-20
Source: https://github.com/lightningnetwork/lnd/commit/667e0aadc3956bc92e65eb2809a9122534554bc1
Type: security-commit

## Details
lnwire: fix test data race

Ensure that tests can run in parallel without causing a data race by
adding a `makeTestChannelUpdate` constructor rather than sharing the
same `testChannelUpdate` type between tests. This is needed since some
tests write to the type.

## Patch
### lnwire/onion_error_test.go
```diff
@@ -14,22 +14,25 @@ import (
 )
 
 var (
-	testOnionHash     = [OnionPacketSize]byte{}
-	testAmount        = MilliSatoshi(1)
-	testCtlvExpiry    = uint32(2)
-	testFlags         = uint16(2)
-	testType          = uint64(3)
-	testOffset        = uint16(24)
-	sig, _            = NewSigFromSignature(testSig)
-	testChannelUpdate = ChannelUpdate1{
+	testOnionHash  = [OnionPacketSize]byte{}
+	testAmount     = MilliSatoshi(1)
+	testCtlvExpiry = uint32(2)
+	testFlags      = uint16(2)
+	testType       = uint64(3)
+	testOffset     = uint16(24)
+	sig, _         = NewSigFromSignature(testSig)
+)
+
+func makeTestChannelUpdate() *ChannelUpdate1 {
+	return &ChannelUpdate1{
 		Signature:       sig,
 		ShortChannelID:  NewShortChanIDFromInt(1),
 		Timestamp:       1,
 		MessageFlags:    0,
 		ChannelFlags:    1,
 		ExtraOpaqueData: make([]byte, 0),
 	}
-)
+}
 
 var onionFailures = []FailureMessage{
 	&FailInvalidRealm{},
@@ -47,13 +50,13 @@ var onionFailures = []FailureMessage{
 	NewInvalidOnionVersion(testOnionHash[:]),
 	NewInvalidOnionHmac(testOnionHash[:]),
 	NewInvalidOnionKey(testOnionHash[:]),
-	NewTemporaryChannelFailure(&testChannelUpdate),
+	NewTemporaryChannelFailure(makeTestChannelUpdate()),
 	NewTemporaryChannelFailure(nil),
-	NewAmountBelowMinimum(testAmount, testChannelUpdate),
-	NewFeeInsufficient(testAmount, testChannelUpdate),
-	NewIncorrectCltvExpiry(testCtlvExpiry, testChannelUpdate),
-	NewExpiryTooSoon(testChannelUpdate),
-	NewChannelDisabled(testFlags, testChannelUpdate),
+	NewAmountBelowMinimum(testAmount, *makeTestChannelUpdate()),
+	NewFeeInsufficient(testAmount, *makeTestChannelUpdate()),
+	NewIncorrectCltvExpiry(testCtlvExpiry, *makeTestChannelUpdate()),
+	NewExpiryTooSoon(*makeTestChannelUpdate()),
+	NewChannelDisabled(testFlags, *makeTestChannelUpdate()),
 	NewFinalIncorrectCltvExpiry(testCtlvExpiry),
 	NewFinalIncorrectHtlcAmount(testAmount),
 	NewInvalidOnionPayload(testType, testOffset),
@@ -128,6 +131,8 @@ func testEncodeDecodeTlv(t *testing.T, testFailure FailureMessage) {
 func TestChannelUpdateCompatibilityParsing(t *testing.T) {
 	t.Parallel()
 
+	testChannelUpdate := *makeTestChannelUpdate()
+
 	// We'll start by taking out test channel update, and encoding it into
 	// a set of raw bytes.
 	var b bytes.Buffer
@@ -146,9 +151,7 @@ func TestChannelUpdateCompatibilityParsing(t *testing.T) {
 
 	// At this point, we'll ensure that we get the exact same failure out
 	// on the other side.
-	if !reflect.DeepEqual(testChannelUpdate, newChanUpdate) {
-		t.Fatalf("mismatched channel updates: %v", err)
-	}
+	require.Equal(t, testChannelUpdate, newChanUpdate)
 
 	// We'll now reset then re-encoded the same channel update to try it in
 	// the proper compatible mode.
@@ -185,7 +188,7 @@ func TestWriteOnionErrorChanUpdate(t *testing.T) {
 	// First, we'll write out the raw channel update so we can obtain the
 	// raw serialized length.
 	var b bytes.Buffer
-	update := testChannelUpdate
+	update := *makeTestChannelUpdate()
 	trueUpdateLength, err := WriteMessage(&b, &update, 0)
 	if err != nil {
 		t.Fatalf("unable to write update: %v", err)
```
