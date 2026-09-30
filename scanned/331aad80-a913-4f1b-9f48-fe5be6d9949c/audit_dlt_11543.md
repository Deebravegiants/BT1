# [?] Protect against accidental nil dereference in EncodeBlob(). (#1404)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2025-03-19
Source: https://github.com/Layr-Labs/eigenda/commit/b074ab51852aa950747016da67f18be37557dd4b
Type: security-commit

## Details
Protect against accidental nil dereference in EncodeBlob(). (#1404)

Signed-off-by: Cody Littley <cody@eigenlabs.org>

## Patch
### disperser/encoder/client_v2.go
```diff
@@ -22,7 +22,12 @@ func NewEncoderClientV2(addr string) (disperser.EncoderClientV2, error) {
 	}, nil
 }
 
-func (c *clientV2) EncodeBlob(ctx context.Context, blobKey corev2.BlobKey, encodingParams encoding.EncodingParams, blobSize uint64) (*encoding.FragmentInfo, error) {
+func (c *clientV2) EncodeBlob(
+	ctx context.Context,
+	blobKey corev2.BlobKey,
+	encodingParams encoding.EncodingParams,
+	blobSize uint64) (*encoding.FragmentInfo, error) {
+
 	// Establish connection
 	conn, err := grpc.NewClient(
 		c.addr,
@@ -54,7 +59,7 @@ func (c *clientV2) EncodeBlob(ctx context.Context, blobKey corev2.BlobKey, encod
 
 	// Extract and return fragment info
 	return &encoding.FragmentInfo{
-		TotalChunkSizeBytes: reply.FragmentInfo.TotalChunkSizeBytes,
-		FragmentSizeBytes:   reply.FragmentInfo.FragmentSizeBytes,
+		TotalChunkSizeBytes: reply.GetFragmentInfo().GetTotalChunkSizeBytes(),
+		FragmentSizeBytes:   reply.GetFragmentInfo().GetFragmentSizeBytes(),
 	}, nil
 }
```
