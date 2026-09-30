# [?] fix(tests/befp): fix panic in befp test (#3108)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2024-01-19
Source: https://github.com/celestiaorg/celestia-node/commit/ba3800969143901d01e52e4509fd02d68ca7f887
Type: security-commit

## Details
fix(tests/befp): fix panic in befp test (#3108)

ShareWithProofs collection happens async and it does not guarantee that
Shares at index [1] will be non-nil. Panic happened in `incorrect share
with Proof` when `befp.Shares[1] == nil`

tested with `go test -v -count=300 -run ^TestBEFP_Validate$
github.com/celestiaorg/celestia-node/share/eds/byzantine`

## Patch
### share/eds/byzantine/bad_encoding_test.go
```diff
@@ -45,7 +45,9 @@ func TestBEFP_Validate(t *testing.T) {
 	var errByz *ErrByzantine
 	require.ErrorAs(t, byzantine, &errByz)
 
-	befp := CreateBadEncodingProof([]byte("hash"), 0, errByz)
+	proof := CreateBadEncodingProof([]byte("hash"), 0, errByz)
+	befp, ok := proof.(*BadEncodingProof)
+	require.True(t, ok)
 	var test = []struct {
 		name           string
 		prepareFn      func() error
@@ -54,7 +56,7 @@ func TestBEFP_Validate(t *testing.T) {
 		{
 			name: "valid BEFP",
 			prepareFn: func() error {
-				return befp.Validate(&header.ExtendedHeader{DAH: &dah})
+				return proof.Validate(&header.ExtendedHeader{DAH: &dah})
 			},
 			expectedResult: func(err error) {
 				require.NoError(t, err)
@@ -88,10 +90,11 @@ func TestBEFP_Validate(t *testing.T) {
 		{
 			name: "incorrect share with Proof",
 			prepareFn: func() error {
-				befp, ok := befp.(*BadEncodingProof)
-				require.True(t, ok)
-				befp.Shares[0].Share = befp.Shares[1].Share
-				return befp.Validate(&header.ExtendedHeader{DAH: &dah})
+				// break the first shareWithProof to test negative case
+				sh := sharetest.RandShares(t, 2)
+				nmtProof := nmt.NewInclusionProof(0, 1, nil, false)
+				befp.Shares[0] = &ShareWithProof{sh[0], &nmtProof}
+				return proof.Validate(&header.ExtendedHeader{DAH: &dah})
 			},
 			expectedResult: func(err error) {
 				require.ErrorIs(t, err, errIncorrectShare)
@@ -100,10 +103,8 @@ func TestBEFP_Validate(t *testing.T) {
 		{
 			name: "invalid amount of shares",
 			prepareFn: func() error {
-				befp, ok := befp.(*BadEncodingProof)
-				require.True(t, ok)
 				befp.Shares = befp.Shares[0 : len(befp.Shares)/2]
-				return befp.Validate(&header.ExtendedHeader{DAH: &dah})
+				return proof.Validate(&header.ExtendedHeader{DAH: &dah})
 			},
 			expectedResult: func(err error) {
 				require.ErrorIs(t, err, errIncorrectAmountOfShares)
@@ -112,10 +113,8 @@ func TestBEFP_Validate(t *testing.T) {
 		{
 			name: "not enough shares to recompute the root",
 			prepareFn: func() error {
-				befp, ok := befp.(*BadEncodingProof)
-				require.True(t, ok)
 				befp.Shares[0] = nil
-				return befp.Validate(&header.ExtendedHeader{DAH: &dah})
+				return proof.Validate(&header.ExtendedHeader{DAH: &dah})
 			},
 			expectedResult: func(err error) {
 				require.ErrorIs(t, err, errIncorrectAmountOfShares)
@@ -124,11 +123,8 @@ func TestBEFP_Validate(t *testing.T) {
 		{
 			name: "index out of bounds",
 			prepareFn: func() error {
-				befp, ok := befp.(*BadEncodingProof)
-				require.True(t, ok)
-				befpCopy := *befp
-				befpCopy.Index = 100
-				return befpCopy.Validate(&header.ExtendedHeader{DAH: &dah})
+				befp.Index = 100
+				return proof.Validate(&header.ExtendedHeader{DAH: &dah})
 			},
 			expectedResult: func(err error) {
 				require.ErrorIs(t, err, errIncorrectIndex)
@@ -137,7 +133,7 @@ func TestBEFP_Validate(t *testing.T) {
 		{
 			name: "heights mismatch",
 			prepareFn: func() error {
-				return befp.Validate(&header.ExtendedHeader{
+				return proof.Validate(&header.ExtendedHeader{
 					RawHeader: core.Header{
 						Height: 42,
 					},
```
