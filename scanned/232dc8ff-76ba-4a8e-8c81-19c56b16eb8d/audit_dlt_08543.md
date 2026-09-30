# [?] catchpointdump: fix panic when processing gzip files (#5210)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2023-03-17
Source: https://github.com/algorand/go-algorand/commit/6cad66e41b38108ec86c7e5249df36bca7813030
Type: security-commit

## Details
catchpointdump: fix panic when processing gzip files (#5210)

## Patch
### cmd/catchpointdump/file.go
```diff
@@ -167,31 +167,36 @@ func isGzipCompressed(catchpointReader *bufio.Reader, catchpointFileSize int64)
 	return prefixBytes[0] == gzipPrefix[0] && prefixBytes[1] == gzipPrefix[1]
 }
 
-func getCatchpointTarReader(catchpointReader *bufio.Reader, catchpointFileSize int64) (*tar.Reader, error) {
+func getCatchpointTarReader(catchpointReader *bufio.Reader, catchpointFileSize int64) (*tar.Reader, bool, error) {
 	if isGzipCompressed(catchpointReader, catchpointFileSize) {
 		gzipReader, err := gzip.NewReader(catchpointReader)
 		if err != nil {
-			return nil, err
+			return nil, false, err
 		}
-
-		return tar.NewReader(gzipReader), nil
+		return tar.NewReader(gzipReader), true, nil
 	}
 
-	return tar.NewReader(catchpointReader), nil
+	return tar.NewReader(catchpointReader), false, nil
 }
 
 func loadCatchpointIntoDatabase(ctx context.Context, catchupAccessor ledger.CatchpointCatchupAccessor, catchpointFile io.Reader, catchpointFileSize int64) (fileHeader ledger.CatchpointFileHeader, err error) {
 	fmt.Printf("\n")
-	printLoadCatchpointProgressLine(0, 50, 0)
+	const barLength = 50
+	printLoadCatchpointProgressLine(0, barLength, 0)
 	lastProgressUpdate := time.Now()
 	progress := uint64(0)
 	defer printLoadCatchpointProgressLine(0, 0, 0)
 
 	catchpointReader := bufio.NewReader(catchpointFile)
-	tarReader, err := getCatchpointTarReader(catchpointReader, catchpointFileSize)
+	tarReader, isCompressed, err := getCatchpointTarReader(catchpointReader, catchpointFileSize)
 	if err != nil {
 		return fileHeader, err
 	}
+	if isCompressed {
+		// gzip'ed file is about 3-6 times smaller than tar
+		// modify catchpointFileSize to make the progress bar more-less reflecting the state
+		catchpointFileSize = 4 * catchpointFileSize
+	}
 
 	var downloadProgress ledger.CatchpointCatchupAccessorProgress
 	for {
@@ -229,7 +234,11 @@ func loadCatchpointIntoDatabase(ctx context.Context, catchupAccessor ledger.Catc
 		}
 		if time.Since(lastProgressUpdate) > 50*time.Millisecond && catchpointFileSize > 0 {
 			lastProgressUpdate = time.Now()
-			printLoadCatchpointProgressLine(int(float64(progress)*50.0/float64(catchpointFileSize)), 50, int64(progress))
+			progressRatio := int(float64(progress) * barLength / float64(catchpointFileSize))
+			if progressRatio > barLength {
+				progressRatio = barLength
+			}
+			printLoadCatchpointProgressLine(progressRatio, barLength, int64(progress))
 		}
 	}
 }
```
