# [?] [libs/autofile] fix DATA RACE by removing openFile() call (#2539)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2018-10-04
Source: https://github.com/cometbft/cometbft/commit/5b1b1ea58a5515545e7efd668a58b2b4d9ba3968
Type: security-commit

## Details
[libs/autofile] fix DATA RACE by removing openFile() call (#2539)

There's a time window after we call RotateFile() where autofile#index+1
does not exist. It will be created during the next call to Write(). BUT
if somebody calls NewReader() before Write(), it will fail with "open
  /tmp/wal#index+1/wal: no such file or directory"

We must create file (either by calling gr.Head.openFile() or directly)
during NewReader() to ensure read calls succeed.

Closes #2538

## Patch
### libs/autofile/group.go
```diff
@@ -280,7 +280,7 @@ func (g *Group) RotateFile() {
 	headPath := g.Head.Path
 
 	if err := g.headBuf.Flush(); err != nil {
-		panic(err) //panic is used for consistent with below
+		panic(err)
 	}
 
 	if err := g.Head.Sync(); err != nil {
@@ -296,12 +296,6 @@ func (g *Group) RotateFile() {
 		panic(err)
 	}
 
-	//make sure head file exist, there is a window time between rename and next write
-	//when NewReader(maxIndex), lead to "open /tmp/wal058868562/wal: no such file or directory"
-	if err := g.Head.openFile(); err != nil {
-		panic(err)
-	}
-
 	g.maxIndex++
 }
 
@@ -684,7 +678,6 @@ func (gr *GroupReader) ReadLine() (string, error) {
 // IF index > gr.Group.maxIndex, returns io.EOF
 // CONTRACT: caller should hold gr.mtx
 func (gr *GroupReader) openFile(index int) error {
-
 	// Lock on Group to ensure that head doesn't move in the meanwhile.
 	gr.Group.mtx.Lock()
 	defer gr.Group.mtx.Unlock()
@@ -694,7 +687,7 @@ func (gr *GroupReader) openFile(index int) error {
 	}
 
 	curFilePath := filePathForIndex(gr.Head.Path, index, gr.Group.maxIndex)
-	curFile, err := os.Open(curFilePath)
+	curFile, err := os.OpenFile(curFilePath, os.O_RDONLY|os.O_CREATE, autoFilePerms)
 	if err != nil {
 		return err
 	}
```
