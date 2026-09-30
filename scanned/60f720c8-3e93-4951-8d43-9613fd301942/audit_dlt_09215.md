# [?] ipfswatch: fix panic on broken link (#11145)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2026-01-14
Source: https://github.com/ipfs/kubo/commit/4bdc9ad22011cab1c58332e69e9889affb95b7f2
Type: security-commit

## Details
ipfswatch: fix panic on broken link (#11145)

Fix panic when broken link is created in watch directory.

Closes #10017

## Patch
### cmd/ipfswatch/main.go
```diff
@@ -150,6 +150,7 @@ func run(ipfsPath, watchPath string) error {
 			log.Printf("received event: %s", e)
 			isDir, err := IsDirectory(e.Name)
 			if err != nil {
+				log.Println(err)
 				continue
 			}
 			switch e.Op {
@@ -220,7 +221,7 @@ func addTree(w *fsnotify.Watcher, root string) error {
 			return filepath.SkipDir
 		case isDir:
 			log.Println(path)
-			if err := w.Add(path); err != nil {
+			if err = w.Add(path); err != nil {
 				return err
 			}
 		default:
@@ -233,7 +234,10 @@ func addTree(w *fsnotify.Watcher, root string) error {
 
 func IsDirectory(path string) (bool, error) {
 	fileInfo, err := os.Stat(path)
-	return fileInfo.IsDir(), err
+	if err != nil {
+		return false, err
+	}
+	return fileInfo.IsDir(), nil
 }
 
 func IsHidden(path string) bool {
```
