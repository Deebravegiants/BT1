# [?] Merge "[FAB-16571] Fix peer panic when package java chaincode"

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2019-09-13
Source: https://github.com/hyperledger/fabric/commit/39176f0dc10e7674c3ade5287e4ce06b69b02b7d
Type: security-commit

## Details
Merge "[FAB-16571] Fix peer panic when package java chaincode"

## Patch
### core/chaincode/platforms/util/writer.go
```diff
@@ -49,6 +49,10 @@ func WriteFolderToTarPackage(tw *tar.Writer, srcPath string, excludeDirs []strin
 
 	rootDirLen := len(rootDirectory)
 	walkFn := func(localpath string, info os.FileInfo, err error) error {
+		if err != nil {
+			vmLogger.Errorf("Visit %s failed: %s", localpath, err)
+			return err
+		}
 
 		// If localpath includes .git, ignore
 		if strings.Contains(localpath, ".git") {
```

### core/chaincode/platforms/util/writer_test.go
```diff
@@ -201,6 +201,26 @@ func TestWriteFolderToTarPackageFailure3(t *testing.T) {
 	gw.Close()
 }
 
+// Failure case 4: with lstat failed
+func Test_WriteFolderToTarPackageFailure4(t *testing.T) {
+	tempDir, err := ioutil.TempDir("", "WriteFolderToTarPackageFailure4BadFileMode")
+	require.NoError(t, err)
+	defer os.RemoveAll(tempDir)
+	testFile := filepath.Join(tempDir, "test.java")
+	err = ioutil.WriteFile(testFile, []byte("Content"), 0644)
+	require.NoError(t, err, "Error creating file", testFile)
+	err = os.Chmod(tempDir, 0644)
+	require.NoError(t, err)
+
+	buf := bytes.NewBuffer(nil)
+	tw := tar.NewWriter(buf)
+	defer tw.Close()
+
+	err = WriteFolderToTarPackage(tw, tempDir, []string{}, nil, nil)
+	assert.Error(t, err, "Should have received error writing folder to package")
+	assert.Contains(t, err.Error(), "permission denied")
+}
+
 func createTestTar(t *testing.T, srcPath string, excludeDir []string, includeFileTypeMap map[string]bool, excludeFileTypeMap map[string]bool) []byte {
 	buf := bytes.NewBuffer(nil)
 	gw := gzip.NewWriter(buf)
```
