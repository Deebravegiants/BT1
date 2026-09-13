# [?] fix(mfs): fix fsync deadlock, set attrs, disable default caching (#11255)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2026-04-02
Source: https://github.com/ipfs/kubo/commit/33e73a6cb64d8b618aed4220f15da3e5a0525183
Type: security-commit

## Details
fix(mfs): fix fsync deadlock, set attrs, disable default caching (#11255)

* fix(MFS): fix deadlock, attrs, caching

* unmount ipns and mfs in mount tests; allow offline

* set attrs Uid, Gid, and Valid for readonly and /ipns

* doc: update changelog

* fix(fuse): maximize kernel cache for immutable /ipfs paths

/ipfs content is addressed by CID and never changes, so kernel
attribute caching is safe and avoids unnecessary FUSE round-trips.
Also sets uid/gid on Root.Attr for consistency.

* docs: move FUSE changelog to v0.41 highlights

* fix(fuse): make IPNS fsync a no-op

Calling fsync on a file opened through /ipns deadlocks and eventually
panics, taking down the entire IPNS mount.

The Fsync handler called mfs.File.Flush(), which tries to open a
second write descriptor on the same file. Only one write descriptor
can exist at a time (desclock is exclusive), and the first one from
Open is still held. The new one blocks forever waiting for the lock.
After the FUSE timeout, Release tries to close the original descriptor
and hits a nil pointer panic in DagModifier.Sync.

Make Fsync a no-op, matching the MFS mount. Data gets flushed when
the file is closed. Also improve the MFS Fsync comment to explain
the same constraint.

* fix(fuse): set uid/gid on IPNS symlinks

The "local" symlink in /ipns showed uid=0 gid=0 (root) while
directories and files showed the daemon's uid/gid. Set uid/gid
and disable attr caching to match other mutable IPNS nodes.

Also add TODO comments across all three FUSE mounts for using
Mode and Mtime from UnixFS records when present, and for wiring
IPNS record TTL into attr cache duration.

* fix(fuse): return empty listing for empty directories

IPNS Directory.ReadDirAll and readonly Node.ReadDirAll returned
ENOENT when a directory had no children. An empty directory still
exists, it just has nothing in it. Return an empty slice instead.

MFS already handles this correctly. The readonly Root.ReadDirAll
correctly returns EPERM (you can't list all of /ipfs). The IPNS
Root.ReadDirAll always has entries (peer keys), so it was never
affected.

This matters for /ipfs because empty directories are valid
content-addressed objects (e.g. QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn
is a well-known CID of an empty UnixFS directory).

* fix(fuse): always sync MFS writes to root on close

The Sync flag was computed as `req.Flags|fuse.OpenSync > 0` (bitwise
OR), which is always true because fuse.OpenSync is non-zero. Replace
with an explicit `true` to match the IPNS mount and make the intent
clear: FUSE writes must always propagate to the MFS root when the
file is closed, regardless of whether the caller set O_SYNC.

* docs: update FUSE changelog for new fixes

* test(fuse): add empty directory listing tests

Verify that listing an empty directory returns an empty result
instead of an error, for all three FUSE mounts:

- /mfs: empty root + empty subdirectory
- /ipns: empty peer directory + empty subdirectory
- /ipfs: empty UnixFS directory added to the DAG

* test(fuse): add append and byte-at-a-time write tests for MFS

IPNS had TestAppendFile and TestMultiWrite but MFS did not. Add
matching tests to cover appending to an existing file and writing
one byte at a time.

* ci(fuse): add dedicated FUSE test job with auto-detection

Add a fuse-tests CI job that installs fuse3, sets TEST_FUSE=1, and
runs FUSE unit tests. Previously these tests were compiled out by
the nofuse build tag (set when TEST_FUSE=0 in the unit-tests job).

Introduce fuse/fusetest package with shared test helpers:

- SkipUnlessFUSE: respects TEST_FUSE env var (0=skip, 1=run) with
  auto-detection fallback that checks for fusermount in PATH
- MountError: fatals when TEST_FUSE=1 (CI expects FUSE to work),
  skips when auto-detecting (local dev without FUSE)

Replace the old ci.NoFuse() (checked TEST_NO_FUSE, a dead env var
nobody set) and per-file maybeSkipFuseTests wrappers.

On Linux, bazil.org/fuse hardcodes "fusermount" but modern distros
only ship "fusermount3". The CI job creates a symlink; the
auto-detect gives a helpful skip message when only fusermount3 is
found locally.

* fix(fuse): handle EINTR on close in IPNS concurrent write test

TestConcurrentWrites was flaky because Go's goroutine preemption
signal (SIGURG) can interrupt the FUSE FLUSH inside close(),
returning EINTR. The write itself already succeeded and the kernel
will still send RELEASE to the daemon, so the data is safe.

Replace os.WriteFile with explicit open/write/close so we can
ignore EINTR on close while still catching real errors.

* fix(fuse): resolve bare file CIDs on /ipfs mount

Accessing a file by its CID at the /ipfs FUSE mount root returned
ENOENT because ProtoNodeConverter cannot handle UnixFS file ADLs.
Decode dag-pb blocks directly from bytes instead.

Closes https://github.com/ipfs/kubo/issues/9044

* fix(fuse): fix same-directory rename on /mfs

Renaming a file within the same MFS directory left the source behind.
The directory's entry cache was re-synced before the old name was
removed. Unlink the source before AddChild to match the working
IPNS pattern.

* test(fuse): add mixed dag-pb/raw directory test

Covers the scenario from https://github.com/ipfs/kubo/issues/9044:
a directory with both dag-pb and raw-leaf children read through
the /ipfs FUSE mount.

* test(fuse): remove redundant testing.Short() checks

SkipUnlessFUSE(t) already handles skipping via TEST_FUSE.
The testing.Short() guard was a second skip gate that served
no purpose since FUSE tests only run under make test_fuse.

* fix(fuse): get DAG node before unlinking source in rename

Move GetNode() before Unlink() in both mfs and ipns Rename
so that a GetNode() failure does not leave the source entry
already removed. Also add FUSE test instructions to AGENTS.md.

* ci: skip fuse3 install when fusermount exists

Self-hosted runners persist state, so after the first run
fuse3 and the symlink are already in place. Skip apt-get
update and install entirely when fusermount is in PATH.

---------

Co-authored-by: Andrew Gillis <11790789+gammazero@users.noreply.github.com>
Co-authored-by: Marcin Rataj <lidel@lidel.org>

### .github/workflows/gotest.yml
```diff
@@ -149,6 +149,35 @@ jobs:
         run: cat test/cli/cli-tests.md >> $GITHUB_STEP_SUMMARY
         if: failure() || success()
 
+  # FUSE filesystem tests (require /dev/fuse and fusermount)
+  fuse-tests:
+    if: github.repository == 'ipfs/kubo' || github.event_name == 'workflow_dispatch'
+    runs-on: ${{ fromJSON(github.repository == 'ipfs/kubo' && '["self-hosted", "linux", "x64", "2xlarge"]' || '"ubuntu-latest"') }}
+    timeout-minutes: 5
+    env:
+      GOTRACEBACK: single
+      TEST_FUSE: 1
+    defaults:
+      run:
+        shell: bash
+    steps:
+      - name: Check out Kubo
+        uses: actions/checkout@v6
+      - name: Set up Go
+        uses: actions/setup-go@v6
+        with:
+          go-version-file: 'go.mod'
+      - name: Install FUSE
+        run: |
+          if ! command -v fusermount &>/dev/null; then
+            sudo apt-get update
+            sudo apt-get install -y fuse3
+            # bazil.org/fuse looks for "fusermount", fuse3 only ships "fusermount3"
+            sudo ln -sf /usr/bin/fusermount3 /usr/local/bin/fusermount
+          fi
+      - name: Run FUSE tests
+        run: make test_fuse
+
   # Example tests (kubo-as-a-library)
   example-tests:
     if: github.repository == 'ipfs/kubo' || github.event_name == 'workflow_dispatch'
```

### AGENTS.md
```diff
@@ -93,6 +93,7 @@ The full test suite is composed of several targets:
 | `make test_short`    | fast subset (`test_go_fmt` + `test_unit`)                             |
 | `make test_unit`     | unit tests with coverage (excludes `test/cli`)                        |
 | `make test_cli`      | CLI integration tests (requires `make build` first)                   |
+| `make test_fuse`     | FUSE filesystem tests (requires `/dev/fuse` and `fusermount` in PATH) |
 | `make test_sharness` | legacy shell-based integration tests                                  |
 | `make test_go_fmt`   | checks Go source formatting                                          |
 | `make -O test_go_lint` | runs `golangci-lint`                                                |
@@ -121,6 +122,16 @@ export IPFS_PATH="$(mktemp -d)"
 
 If you see "version (N) is lower than repos (M)", the `ipfs` binary in `PATH` is outdated. Rebuild with `make build` and verify `PATH`.
 
+### Running FUSE Tests
+
+FUSE tests require `/dev/fuse` and `fusermount` in `PATH`. On systems with only fuse3, create a symlink:
+
+```bash
+ln -s /usr/bin/fusermount3 /tmp/fusermount && PATH="/tmp:$PATH" make test_fuse
+```
+
+Set `TEST_FUSE=1` to make mount failures fatal (CI does this). Without it, tests auto-detect and skip when FUSE is unavailable.
+
 ### Running Sharness Tests
 
 Sharness tests are legacy shell-based tests. Run individual tests with a timeout:
@@ -144,8 +155,10 @@ pkill -f "ipfs daemon"
 - all new integration tests go in `test/cli/`, not `test/sharness/`
 - if a `test/sharness` test needs significant changes, remove it and add a replacement in `test/cli/`
 - use [testify](https://github.com/stretchr/testify) for assertions (already a dependency)
+- use `t.Context()` instead of `context.Background()` in tests
 - for Go 1.25+, use `testing/synctest` when testing concurrent code (goroutines, channels, timers)
 - reuse existing `.car` fixtures in `test/cli/fixtures/` when possible; only add new fixtures when the test requires data not covered by existing ones
+- when writing tests that cover CIDv0 vs CIDv1, always set the CID version explicitly (never rely on defaults); if chunk size matters for the test, also set the chunker explicitly
 - always re-run modified tests locally before submitting to confirm they pass
 - avoid emojis in test names and test log output
 
```

### Rules.mk
```diff
@@ -138,6 +138,7 @@ help:
 	@echo '  test_short              - Run fast tests (test_go_fmt, test_unit)'
 	@echo '  test_unit               - Run unit tests with coverage (excludes test/cli)'
 	@echo '  test_cli                - Run CLI integration tests (requires built binary)'
+	@echo '  test_fuse               - Run FUSE tests (requires /dev/fuse and fusermount)'
 	@echo '  test_go_fmt             - Check Go source formatting'
 	@echo '  test_go_build           - Build kubo for all platforms from .github/build-platforms.yml'
 	@echo '  test_go_lint            - Run golangci-lint'
```

### docs/changelogs/v0.41.md
```diff
@@ -15,6 +15,7 @@ This release was brought to you by the [Shipyard](https://ipshipyard.com/) team.
   - [🖥️ WebUI Improvements](#-webui-improvements)
   - [🔧 Correct provider addresses for custom HTTP routing](#-correct-provider-addresses-for-custom-http-routing)
   - [`ipfs object patch` validates UnixFS node types](#ipfs-object-patch-validates-unixfs-node-types)
+  - [📂 FUSE Mount Fixes](#-fuse-mount-fixes)
   - [📦️ Dependency updates](#-dependency-updates)
 - [📝 Changelog](#-changelog)
 - [👨‍👩‍👧‍👦 Contributors](#-contributors)
@@ -98,6 +99,18 @@ directory types correctly, including large sharded directories.
 
 A `--allow-non-unixfs` flag is available on both `ipfs object patch` commands to bypass validation.
 
+#### 📂 FUSE Mount Fixes
+
+FUSE mounts (`/ipfs`, `/ipns`, `/mfs`) now work with editors like VIM that rely on `fsync` and expect standard file ownership. FUSE support is still experimental. If you run into problems, please report them at [kubo/issues](https://github.com/ipfs/kubo/issues).
+
+- **No more deadlocks on save.** Editors that call `fsync` after writing would hang indefinitely on `/mfs` and `/ipns` mounts. `Fsync` is now a no-op on both; data is flushed when the file descriptor is closed.
+- **Files are no longer owned by root.** Mounts now report the uid/gid of the daemon process, so access works without `allow_other`.
+- **Offline IPNS writes succeed.** Writing through `/ipns` FUSE mounts no longer fails when the node has no network. IPNS records are stored locally and published when connectivity returns.
+- **Smarter kernel caching.** Attribute caching is disabled for mutable mounts (`/ipns`, `/mfs`) to prevent stale reads after writes. Immutable `/ipfs` paths use long-lived caching since content addressed by CID never changes.
+- **Empty directories list correctly.** Listing an empty directory on `/ipfs` or `/ipns` no longer returns an error.
+- **Bare file CIDs work on `/ipfs`.** Accessing a file by its CID directly under the `/ipfs` mount (e.g. `/ipfs/<CID>`) no longer returns "not found". This was a [long-standing regression](https://github.com/ipfs/kubo/issues/9044) that only affected files; directories were not affected.
+- **Rename works on `/mfs`.** Renaming a file within the same directory no longer leaves the source behind.
+
 #### 📦️ Dependency updates
 
 - update `go-libp2p` to [v0.48.0](https://github.com/libp2p/go-libp2p/releases/tag/v0.48.0)
```

### fuse/fusetest/detect.go
```diff
@@ -0,0 +1,57 @@
+//go:build !nofuse
+
+package fusetest
+
+import (
+	"os"
+	"os/exec"
+	"runtime"
+	"testing"
+)
+
+// fuseFlagFromEnv returns the value of TEST_FUSE if set, or empty string.
+// Also checks the legacy TEST_NO_FUSE for backwards compatibility.
+func fuseFlagFromEnv() string {
+	if v := os.Getenv("TEST_FUSE"); v != "" {
+		return v
+	}
+	// Legacy: TEST_NO_FUSE=1 is equivalent to TEST_FUSE=0
+	if os.Getenv("TEST_NO_FUSE") == "1" {
+		return "0"
+	}
+	return ""
+}
+
+// fuseAvailable checks whether FUSE is likely to work on this system
+// and skips with a helpful message if not.
+//
+// On Linux, bazil.org/fuse requires "fusermount" (not "fusermount3") in
+// PATH. Systems with only fuse3 installed need a symlink:
+//
+//	sudo ln -s /usr/bin/fusermount3 /usr/local/bin/fusermount
+func fuseAvailable(t *testing.T) bool {
+	t.Helper()
+
+	switch runtime.GOOS {
+	case "linux", "darwin", "freebsd", "netbsd", "openbsd":
+	default:
+		t.Skip("FUSE not supported on", runtime.GOOS)
+		return false
+	}
+
+	if runtime.GOOS == "linux" {
+		if _, err := exec.LookPath("fusermount"); err == nil {
+			return true
+		}
+		if _, err := exec.LookPath("fusermount3"); err == nil {
+			t.Skip("fusermount3 found but bazil.org/fuse needs \"fusermount\"; create a symlink: sudo ln -s /usr/bin/fusermount3 /usr/local/bin/fusermount")
+		}
+		t.Skip("fusermount not found in PATH")
+		return false
+	}
+
+	if _, err := exec.LookPath("umount"); err != nil {
+		t.Skip("umount not found in PATH")
+	}
+	return true
+}
```

### fuse/fusetest/fusetest.go
```diff
@@ -0,0 +1,42 @@
+//go:build !nofuse
+
+// Package fusetest provides test helpers shared across FUSE test packages.
+package fusetest
+
+import (
+	"testing"
+)
+
+// SkipUnlessFUSE skips the test when FUSE is not available.
+//
+// Decision order:
+//  1. TEST_FUSE=0 (or legacy TEST_NO_FUSE=1) → skip
+//  2. TEST_FUSE=1 → run (CI should set this after installing fuse3)
+//  3. Neither set → auto-detect based on platform and fusermount in PATH;
+//     skip with a helpful message if not found
+func SkipUnlessFUSE(t *testing.T) {
+	t.Helper()
+
+	if v := fuseFlagFromEnv(); v != "" {
+		if v == "0" {
+			t.Skip("FUSE tests disabled (TEST_FUSE=0)")
+		}
+		return // TEST_FUSE=1, run unconditionally
+	}
+
+	fuseAvailable(t) // skips with a helpful message if not available
+}
+
+// MountError handles a FUSE mount error. When TEST_FUSE=1 (CI), a mount
+// failure is fatal because the environment is expected to have working FUSE.
+// When auto-detecting (no TEST_FUSE set), mount failures cause a skip.
+func MountError(t *testing.T, err error) {
+	t.Helper()
+	if err == nil {
+		return
+	}
+	if fuseFlagFromEnv() == "1" {
+		t.Fatal("FUSE mount failed (TEST_FUSE=1, expected FUSE to work):", err)
+	}
+	t.Skip("FUSE mount failed:", err)
+}
```

### fuse/ipns/ipns_test.go
```diff
@@ -5,30 +5,24 @@ package ipns
 import (
 	"bytes"
 	"context"
+	"errors"
 	"fmt"
 	"io"
 	mrand "math/rand"
 	"os"
 	"sync"
+	"syscall"
 	"testing"
 
-	"bazil.org/fuse"
-
 	core "github.com/ipfs/kubo/core"
 	coreapi "github.com/ipfs/kubo/core/coreapi"
 
 	fstest "bazil.org/fuse/fs/fstestutil"
 	racedet "github.com/ipfs/go-detect-race"
 	"github.com/ipfs/go-test/random"
-	ci "github.com/libp2p/go-libp2p-testing/ci"
+	"github.com/ipfs/kubo/fuse/fusetest"
 )
 
-func maybeSkipFuseTests(t *testing.T) {
-	if ci.NoFuse() {
-		t.Skip("Skipping FUSE tests")
-	}
-}
-
 func randBytes(size int) []byte {
 	b := make([]byte, size)
 	_, err := io.ReadFull(random.NewRand(), b)
@@ -55,8 +49,27 @@ func writeFileOrFail(t *testing.T, size int, path string) []byte {
 
 func writeFile(size int, path string) ([]byte, error) {
 	data := randBytes(size)
-	err := os.WriteFile(path, data, 0o666)
-	return data, err
+	// Same flags as os.WriteFile: write-only, create if missing, truncate if exists.
+	// We open manually instead of using os.WriteFile so we can handle EINTR on close.
+	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0o666)
+	if err != nil {
+		return nil, err
+	}
+	_, err = f.Write(data)
+	if err != nil {
+		f.Close()
+		return nil, err
+	}
+	// Go's goroutine preemption (SIGURG) can interrupt the FUSE FLUSH
+	// inside close(), returning EINTR. This is not a data loss: the write
+	// already succeeded and the kernel will still send RELEASE to the FUSE
+	// daemon. Go intentionally does not retry close() on EINTR because the
+	// fd is already closed on Linux and its state is undefined on other
+	// platforms, making retry unsafe.
+	if err := f.Close(); err != nil && !errors.Is(err, syscall.EINTR) {
+		return nil, err
+	}
+	return data, nil
 }
 
 func verifyFile(t *testing.T, path string, wantData []byte) {
@@ -100,7 +113,7 @@ func (m *mountWrap) Close() error {
 
 func setupIpnsTest(t *testing.T, node *core.IpfsNode) (*core.IpfsNode, *mountWrap) {
 	t.Helper()
-	maybeSkipFuseTests(t)
+	fusetest.SkipUnlessFUSE(t)
 
 	var err error
 	if node == nil {
@@ -125,12 +138,7 @@ func setupIpnsTest(t *testing.T, node *core.IpfsNode) (*core.IpfsNode, *mountWra
 		t.Fatal(err)
 	}
 	mnt, err := fstest.MountedT(t, fs, nil)
-	if err == fuse.ErrOSXFUSENotFound {
-		t.Skip(err)
-	}
-	if err != nil {
-		t.Fatalf("error mounting at temporary directory: %v", err)
-	}
+	fusetest.MountError(t, err)
 
 	return node, &mountWrap{
 		Mount: mnt,
@@ -155,11 +163,37 @@ func TestIpnsLocalLink(t *testing.T) {
 	}
 }
 
+// Test that empty directories can be listed without errors.
+func TestEmptyDirListing(t *testing.T) {
+	nd, mnt := setupIpnsTest(t, nil)
+	defer mnt.Close()
+
+	// The peer's IPNS directory starts empty.
+	peerDir := mnt.Dir + "/" + nd.Identity.String()
+	entries, err := os.ReadDir(peerDir)
+	if err != nil {
+		t.Fatal(err)
+	}
+	if len(entries) != 0 {
+		t.Fatalf("expected empty peer dir, got %d entries", len(entries))
+	}
+
+	// Create a subdirectory and list it while still empty.
+	subdir := peerDir + "/emptydir"
+	if err := os.Mkdir(subdir, os.ModeDir); err != nil {
+		t.Fatal(err)
+	}
+	entries, err = os.ReadDir(subdir)
+	if err != nil {
+		t.Fatal(err)
+	}
+	if len(entries) != 0 {
+		t.Fatalf("expected empty subdirectory, got %d entries", len(entries))
+	}
+}
+
 // Test writing a file and reading it back.
 func TestIpnsBasicIO(t *testing.T) {
-	if testing.Short() {
-		t.SkipNow()
-	}
 	nd, mnt := setupIpnsTest(t, nil)
 	defer closeMount(mnt)
 
@@ -186,11 +220,38 @@ func TestIpnsBasicIO(t *testing.T) {
 	}
 }
 
+// Test renaming a file within the same IPNS directory.
+func TestRenameFile(t *testing.T) {
+	nd, mnt := setupIpnsTest(t, nil)
+	defer closeMount(mnt)
+
+	peerDir := mnt.Dir + "/" + nd.Identity.String()
+	src := peerDir + "/before.txt"
+	dst := peerDir + "/after.txt"
+
+	data := writeFileOrFail(t, 500, src)
+
+	if err := os.Rename(src, dst); err != nil {
+		t.Fatal(err)
+	}
+
+	// Source must be gone.
+	if _, err := os.Stat(src); !os.IsNotExist(err) {
+		t.Fatalf("source still exists after rename: %v", err)
+	}
+
+	// Destination must have the original content.
+	got, err := os.ReadFile(dst)
+	if err != nil {
+		t.Fatal(err)
+	}
+	if !bytes.Equal(got, data) {
+		t.Fatalf("content mismatch: got %d bytes, want %d", len(got), len(data))
+	}
+}
+
 // Test to make sure file changes persist over mounts of ipns.
 func TestFilePersistence(t *testing.T) {
-	if testing.Short() {
-		t.SkipNow()
-	}
 	node, mnt := setupIpnsTest(t, nil)
 
 	fname := "/local/atestfile"
@@ -251,9 +312,6 @@ func TestMultipleDirs(t *testing.T) {
 
 // Test to make sure the filesystem reports file sizes correctly.
 func TestFileSizeReporting(t *testing.T) {
-	if testing.Short() {
-		t.SkipNow()
-	}
 	_, mnt := setupIpnsTest(t, nil)
 	defer mnt.Close()
 
@@ -272,9 +330,6 @@ func TestFileSizeReporting(t *testing.T) {
 
 // Test to make sure you can't create multiple entries with the same name.
 func TestDoubleEntryFailure(t *testing.T) {
-	if testing.Short() {
-		t.SkipNow()
-	}
 	_, mnt := setupIpnsTest(t, nil)
 	defer mnt.Close()
 
@@ -291,9 +346,6 @@ func TestDoubleEntryFailure(t *testing.T) {
 }
 
 func TestAppendFile(t *testing.T) {
-	if testing.Short() {
-		t.SkipNow()
-	}
 	_, mnt := setupIpnsTest(t, nil)
 	defer mnt.Close()
 
@@ -332,9 +384,6 @@ func TestAppendFile(t *testing.T) {
 }
 
 func TestConcurrentWrites(t *testing.T) {
-	if testing.Short() {
-		t.SkipNow()
-	}
 	_, mnt := setupIpnsTest(t, nil)
 	defer mnt.Close()
 
@@ -381,9 +430,6 @@ func TestConcurrentWrites(t *testing.T) {
 func TestFSThrash(t *testing.T) {
 	files := make(map[string][]byte)
 
-	if testing.Short() {
-		t.SkipNow()
-	}
 	_, mnt := setupIpnsTest(t, nil)
 	defer mnt.Close()
 
@@ -464,9 +510,6 @@ func TestFSThrash(t *testing.T) {
 
 // Test writing a medium sized file one byte at a time.
 func TestMultiWrite(t *testing.T) {
-	if testing.Short() {
-		t.SkipNow()
-	}
 
 	_, mnt := setupIpnsTest(t, nil)
 	defer mnt.Close()
```

### fuse/ipns/ipns_unix.go
```diff
@@ -86,7 +86,7 @@ type Root struct {
 
 func ipnsPubFunc(ipfs iface.CoreAPI, key iface.Key) mfs.PubFunc {
 	return func(ctx context.Context, c cid.Cid) error {
-		_, err := ipfs.Name().Publish(ctx, path.FromCid(c), options.Name.Key(key.Name()))
+		_, err := ipfs.Name().Publish(ctx, path.FromCid(c), options.Name.Key(key.Name()), options.Name.AllowOffline(true))
 		return err
 	}
 }
@@ -153,7 +153,11 @@ func CreateRoot(ctx context.Context, ipfs iface.CoreAPI, keys map[string]iface.K
 // Attr returns file attributes.
 func (r *Root) Attr(ctx context.Context, a *fuse.Attr) error {
 	log.Debug("Root Attr")
+	// TODO: wire TTL from IPNS record (capped at Ipns.MaxCacheTTL) here instead of 0
+	a.Valid = 0
 	a.Mode = os.ModeDir | 0o111 // -rw+x
+	a.Uid = uint32(os.Getuid())
+	a.Gid = uint32(os.Getgid())
 	return nil
 }
 
@@ -252,6 +256,9 @@ type File struct {
 // Attr returns the attributes of a given node.
 func (d *Directory) Attr(ctx context.Context, a *fuse.Attr) error {
 	log.Debug("Directory Attr")
+	// TODO: wire TTL from IPNS record (capped at Ipns.MaxCacheTTL) here instead of 0
+	a.Valid = 0
+	// TODO: use Mode from UnixFS record if present
 	a.Mode = os.ModeDir | 0o555
 	a.Uid = uint32(os.Getuid())
 	a.Gid = uint32(os.Getgid())
@@ -261,11 +268,14 @@ func (d *Directory) Attr(ctx context.Context, a *fuse.Attr) error {
 // Attr returns the attributes of a given node.
 func (fi *FileNode) Attr(ctx context.Context, a *fuse.Attr) error {
 	log.Debug("File Attr")
+	// TODO: wire TTL from IPNS record (capped at Ipns.MaxCacheTTL) here instead of 0
+	a.Valid = 0
 	size, err := fi.fi.Size()
 	if err != nil {
 		// In this case, the dag node in question may not be unixfs
 		return fmt.Errorf("fuse/ipns: failed to get file.Size(): %s", err)
 	}
+	// TODO: use Mode and Mtime from UnixFS record if present
 	a.Mode = os.FileMode(0o666)
 	a.Size = uint64(size)
 	a.Uid = uint32(os.Getuid())
@@ -313,10 +323,7 @@ func (d *Directory) ReadDirAll(ctx context.Context) ([]fuse.Dirent, error) {
 		entries[i] = dirent
 	}
 
-	if len(entries) > 0 {
-		return entries, nil
-	}
-	return nil, syscall.Errno(syscall.ENOENT)
+	return entries, nil
 }
 
 func (fi *File) Read(ctx context.Context, req *fuse.ReadRequest, resp *fuse.ReadResponse) error {
@@ -381,20 +388,14 @@ func (fi *File) Setattr(ctx context.Context, req *fuse.SetattrRequest, resp *fus
 	return nil
 }
 
-// Fsync flushes the content in the file to disk.
+// Fsync is a no-op. We can't flush here because mfs.File.Flush opens a new
+// write descriptor, which needs an exclusive lock (desclock) that the caller
+// already holds from Open. Attempting it deadlocks until the FUSE timeout,
+// then panics on Release. Data is flushed when the file is closed instead.
+// TODO: a proper fix needs changes in boxo/mfs to allow flushing from an
+// existing descriptor. Ideas welcome, but for now this is the best we can do.
 func (fi *FileNode) Fsync(ctx context.Context, req *fuse.FsyncRequest) error {
-	// This needs to perform a *full* flush because, in MFS, a write isn't
-	// persisted until the root is updated.
-	errs := make(chan error, 1)
-	go func() {
-		errs <- fi.fi.Flush()
-	}()
-	select {
-	case err := <-errs:
-		return err
-	case <-ctx.Done():
-		return ctx.Err()
-	}
+	return nil
 }
 
 func (fi *File) Forget() {
@@ -502,18 +503,21 @@ func (d *Directory) Rename(ctx context.Context, req *fuse.RenameRequest, newDir
 		return err
 	}
 
+	nd, err := cur.GetNode()
+	if err != nil {
+		return err
+	}
+
+	// Unlink the source before adding to the destination. For
+	// same-directory renames, this clears the old name from the
+	// directory's entry cache before AddChild repopulates it.
 	err = d.dir.Unlink(req.OldName)
 	if err != nil {
 		return err
 	}
 
 	switch newDir := newDir.(type) {
 	case *Directory:
-		nd, err := cur.GetNode()
-		if err != nil {
-			return err
-		}
-
 		err = newDir.dir.AddChild(req.NewName, nd)
 		if err != nil {
 			return err
```

### fuse/ipns/link_unix.go
```diff
@@ -16,7 +16,11 @@ type Link struct {
 
 func (l *Link) Attr(ctx context.Context, a *fuse.Attr) error {
 	log.Debug("Link attr.")
+	// TODO: wire TTL from IPNS record (capped at Ipns.MaxCacheTTL) here instead of 0
+	a.Valid = 0
 	a.Mode = os.ModeSymlink | 0o555
+	a.Uid = uint32(os.Getuid())
+	a.Gid = uint32(os.Getgid())
 	return nil
 }
 
```

### fuse/mfs/mfs_test.go
```diff
@@ -19,14 +19,12 @@ import (
 	"bazil.org/fuse/fs/fstestutil"
 	"github.com/ipfs/kubo/core"
 	"github.com/ipfs/kubo/core/node"
-	"github.com/libp2p/go-libp2p-testing/ci"
+	"github.com/ipfs/kubo/fuse/fusetest"
 )
 
 // Create an Ipfs.Node, a filesystem and a mount point.
 func setUp(t *testing.T, ipfs *core.IpfsNode) (fs.FS, *fstestutil.Mount) {
-	if ci.NoFuse() {
-		t.Skip("Skipping FUSE tests")
-	}
+	fusetest.SkipUnlessFUSE(t)
 
 	if ipfs == nil {
 		var err error
@@ -38,12 +36,7 @@ func setUp(t *testing.T, ipfs *core.IpfsNode) (fs.FS, *fstestutil.Mount) {
 
 	fs := NewFileSystem(ipfs)
 	mnt, err := fstestutil.MountedT(t, fs, nil)
-	if err == fuse.ErrOSXFUSENotFound {
-		t.Skip(err)
-	}
-	if err != nil {
-		t.Fatal(err)
-	}
+	fusetest.MountError(t, err)
 
 	return fs, mnt
 }
@@ -90,6 +83,34 @@ func TestReadWrite(t *testing.T) {
 	})
 }
 
+// Test that empty directories can be listed without errors.
+func TestEmptyDirListing(t *testing.T) {
+	_, mnt := setUp(t, nil)
+	defer mnt.Close()
+
+	// The MFS root starts empty.
+	entries, err := os.ReadDir(mnt.Dir)
+	if err != nil {
+		t.Fatal(err)
+	}
+	if len(entries) != 0 {
+		t.Fatalf("expected empty root, got %d entries", len(entries))
+	}
+
+	// Create a directory and list it while still empty.
+	dir := mnt.Dir + "/emptydir"
+	if err := os.Mkdir(dir, os.ModeDir); err != nil {
+		t.Fatal(err)
+	}
+	entries, err = os.ReadDir(dir)
+	if err != nil {
+		t.Fatal(err)
+	}
+	if len(entries) != 0 {
+		t.Fatalf("expected empty directory, got %d entries", len(entries))
+	}
+}
+
 // Test creating a directory.
 func TestMkdir(t *testing.T) {
 	_, mnt := setUp(t, nil)
@@ -294,6 +315,125 @@ func TestConcurrentRW(t *testing.T) {
 	})
 }
 
+// Test appending data to an existing file.
+func TestAppendFile(t *testing.T) {
+	_, mnt := setUp(t, nil)
+	defer mnt.Close()
+
+	path := mnt.Dir + "/appendfile"
+
+	initial := make([]byte, 1300)
+	if _, err := rand.Read(initial); err != nil {
+		t.Fatal(err)
+	}
+	if err := os.WriteFile(path, initial, 0o644); err != nil {
+		t.Fatal(err)
+	}
+
+	fi, err := os.OpenFile(path, os.O_RDWR|os.O_APPEND, 0o644)
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	extra := make([]byte, 500)
+	if _, err := rand.Read(extra); err != nil {
+		t.Fatal(err)
+	}
+
+	n, err := fi.Write(extra)
+	if err != nil {
+		t.Fatal(err)
+	}
+	if n != len(extra) {
+		t.Fatalf("short write: %d != %d", n, len(extra))
+	}
+	if err := fi.Close(); err != nil {
+		t.Fatal(err)
+	}
+
+	got, err := os.ReadFile(path)
+	if err != nil {
+		t.Fatal(err)
+	}
+	want := append(initial, extra...)
+	if !bytes.Equal(got, want) {
+		t.Fatalf("content mismatch: got %d bytes, want %d", len(got), len(want))
+	}
+}
+
+// Test writing a file one byte at a time.
+func TestMultiWrite(t *testing.T) {
+	_, mnt := setUp(t, nil)
+	defer mnt.Close()
+
+	path := mnt.Dir + "/multiwrite"
+	fi, err := os.Create(path)
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	data := make([]byte, 1001)
+	if _, err := rand.Read(data); err != nil {
+		t.Fatal(err)
+	}
+
+	for i := range data {
+		n, err := fi.Write(data[i : i+1])
+		if err != nil {
+			t.Fatal(err)
+		}
+		if n != 1 {
+			t.Fatal("short write")
+		}
+	}
+	if err := fi.Close(); err != nil {
+		t.Fatal(err)
+	}
+
+	got, err := os.ReadFile(path)
+	if err != nil {
+		t.Fatal(err)
+	}
+	if !bytes.Equal(got, data) {
+		t.Fatal("content mismatch")
+	}
+}
+
+// Test renaming a file within the same directory.
+func TestRenameFile(t *testing.T) {
+	_, mnt := setUp(t, nil)
+	defer mnt.Close()
+
+	src := mnt.Dir + "/before.txt"
+	dst := mnt.Dir + "/after.txt"
+
+	data := make([]byte, 500)
+	if _, err := rand.Read(data); err != nil {
+		t.Fatal(err)
+	}
+	if err := os.WriteFile(src, data, 0o644); err != nil {
+		t.Fatal(err)
+	}
+
+	if err := os.Rename(src, dst); err != nil {
+		t.Fatal(err)
+	}
+
+	// Source must be gone.
+	if _, err := os.Stat(src); !os.IsNotExist(err) {
+		t.Fatalf("source still exists after rename: %v", err)
+	}
+
+	// Destination must have the original content.
+	got, err := os.ReadFile(dst)
+	if err != nil {
+		t.Fatal(err)
+	}
+	if !bytes.Equal(got, data) {
+		t.Fatalf("content mismatch: got %d bytes, want %d", len(got), len(data))
+	}
+}
+
 // Test ipfs_cid extended attribute
 func TestMFSRootXattr(t *testing.T) {
 	ipfs, err := core.NewNode(context.Background(), &node.BuildCfg{})
```

### fuse/mfs/mfs_unix.go
```diff
@@ -44,9 +44,13 @@ type Dir struct {
 
 // Directory attributes (stat).
 func (dir *Dir) Attr(ctx context.Context, attr *fuse.Attr) error {
+	attr.Valid = 0
+	// TODO: use Mode from UnixFS record if present
 	attr.Mode = mfsDirMode
 	attr.Size = dirSize * blockSize
 	attr.Blocks = dirSize
+	attr.Uid = uint32(os.Getuid())
+	attr.Gid = uint32(os.Getgid())
 	return nil
 }
 
@@ -61,6 +65,8 @@ func (dir *Dir) Lookup(ctx context.Context, req *fuse.LookupRequest, resp *fuse.
 		return nil, err
 	}
 
+	resp.EntryValid = 0
+
 	switch mfsNode.Type() {
 	case mfs.TDir:
 		result := Dir{
@@ -136,29 +142,29 @@ func (dir *Dir) Remove(ctx context.Context, req *fuse.RemoveRequest) error {
 
 // Move (mv) an MFS file.
 func (dir *Dir) Rename(ctx context.Context, req *fuse.RenameRequest, newDir fs.Node) error {
-	file, err := dir.mfsDir.Child(req.OldName)
+	child, err := dir.mfsDir.Child(req.OldName)
 	if err != nil {
 		return err
 	}
-	node, err := file.GetNode()
+
+	nd, err := child.GetNode()
 	if err != nil {
 		return err
 	}
-	targetDir := newDir.(*Dir)
 
-	// Remove file if exists
-	err = targetDir.mfsDir.Unlink(req.NewName)
-	if err != nil && err != os.ErrNotExist {
+	// Unlink the source first. For same-directory renames, this clears
+	// the old name from the directory's entry cache before AddChild
+	// repopulates it with the new name. Without this ordering, Flush
+	// would sync the stale cache entry back into the DAG.
+	if err := dir.mfsDir.Unlink(req.OldName); err != nil {
 		return err
 	}
 
-	err = targetDir.mfsDir.AddChild(req.NewName, node)
-	if err != nil {
+	targetDir := newDir.(*Dir)
+	if err := targetDir.mfsDir.Unlink(req.NewName); err != nil && err != os.ErrNotExist {
 		return err
 	}
-
-	err = dir.mfsDir.Unlink(req.OldName)
-	if err != nil {
+	if err := targetDir.mfsDir.AddChild(req.NewName, nd); err != nil {
 		return err
 	}
 
@@ -199,7 +205,7 @@ func (dir *Dir) Create(ctx context.Context, req *fuse.CreateRequest, resp *fuse.
 	flags := mfs.Flags{
 		Read:  accessMode == fuse.OpenReadOnly || accessMode == fuse.OpenReadWrite,
 		Write: accessMode == fuse.OpenWriteOnly || accessMode == fuse.OpenReadWrite,
-		Sync:  req.Flags|fuse.OpenSync > 0,
+		Sync:  true, // FUSE writes must propagate to the MFS root on close
 	}
 
 	fd, err := mfsFile.Open(flags)
@@ -241,6 +247,8 @@ type File struct {
 
 // File attributes.
 func (file *File) Attr(ctx context.Context, attr *fuse.Attr) error {
+	attr.Valid = 0
+
 	size, _ := file.mfsFile.Size()
 
 	attr.Size = uint64(size)
@@ -253,7 +261,10 @@ func (file *File) Attr(ctx context.Context, attr *fuse.Attr) error {
 	mtime, _ := file.mfsFile.ModTime()
 	attr.Mtime = mtime
 
+	// TODO: use Mode from UnixFS record if present
 	attr.Mode = mfsFileMode
+	attr.Uid = uint32(os.Getuid())
+	attr.Gid = uint32(os.Getgid())
 	return nil
 }
 
@@ -263,7 +274,7 @@ func (file *File) Open(ctx context.Context, req *fuse.OpenRequest, resp *fuse.Op
 	flags := mfs.Flags{
 		Read:  accessMode == fuse.OpenReadOnly || accessMode == fuse.OpenReadWrite,
 		Write: accessMode == fuse.OpenWriteOnly || accessMode == fuse.OpenReadWrite,
-		Sync:  req.Flags|fuse.OpenSync > 0,
+		Sync:  true, // FUSE writes must propagate to the MFS root on close
 	}
 	fd, err := file.mfsFile.Open(flags)
 	if err != nil {
@@ -281,9 +292,14 @@ func (file *File) Open(ctx context.Context, req *fuse.OpenRequest, resp *fuse.Op
 	}, nil
 }
 
-// Sync the file's contents to MFS.
+// Fsync is a no-op. We can't flush here because mfs.File.Flush opens a new
+// write descriptor, which needs an exclusive lock (desclock) that the caller
+// already holds from Open. Attempting it deadlocks until the FUSE timeout.
+// Data is flushed when the file is closed instead.
+// TODO: a proper fix needs changes in boxo/mfs to allow flushing from an
+// existing descriptor. Ideas welcome, but for now this is the best we can do.
 func (file *File) Fsync(ctx context.Context, req *fuse.FsyncRequest) error {
-	return file.mfsFile.Sync()
+	return nil
 }
 
 // List file xattr.
```

### fuse/node/mount_test.go
```diff
@@ -5,25 +5,15 @@ package node
 import (
 	"context"
 	"os"
-	"strings"
 	"testing"
 	"time"
 
-	"bazil.org/fuse"
-
 	core "github.com/ipfs/kubo/core"
+	"github.com/ipfs/kubo/fuse/fusetest"
 	ipns "github.com/ipfs/kubo/fuse/ipns"
 	mount "github.com/ipfs/kubo/fuse/mount"
-
-	ci "github.com/libp2p/go-libp2p-testing/ci"
 )
 
-func maybeSkipFuseTests(t *testing.T) {
-	if ci.NoFuse() {
-		t.Skip("Skipping FUSE tests")
-	}
-}
-
 func mkdir(t *testing.T, path string) {
 	err := os.Mkdir(path, os.ModeDir|os.ModePerm)
 	if err != nil {
@@ -33,12 +23,9 @@ func mkdir(t *testing.T, path string) {
 
 // Test externally unmounting, then trying to unmount in code.
 func TestExternalUnmount(t *testing.T) {
-	if testing.Short() {
-		t.SkipNow()
-	}
 
 	// TODO: needed?
-	maybeSkipFuseTests(t)
+	fusetest.SkipUnlessFUSE(t)
 
 	node, err := core.NewNode(context.Background(), &core.BuildCfg{})
 	if err != nil {
@@ -61,15 +48,20 @@ func TestExternalUnmount(t *testing.T) {
 	mkdir(t, mfsDir)
 
 	err = Mount(node, ipfsDir, ipnsDir, mfsDir)
-	if err != nil {
-		if strings.Contains(err.Error(), "unable to check fuse version") || err == fuse.ErrOSXFUSENotFound {
-			t.Skip(err)
-		}
-	}
+	fusetest.MountError(t, err)
 
-	if err != nil {
-		t.Fatalf("error mounting: %v", err)
-	}
+	t.Cleanup(func() {
+		if node.Mounts.Mfs != nil && node.Mounts.Mfs.IsActive() {
+			if err := node.Mounts.Mfs.Unmount(); err != nil {
+				t.Fatal(err)
+			}
+		}
+		if node.Mounts.Ipns != nil && node.Mounts.Ipns.IsActive() {
+			if err := node.Mounts.Ipns.Unmount(); err != nil {
+				t.Fatal(err)
+			}
+		}
+	})
 
 	// Run shell command to externally unmount the directory
 	cmd, err := mount.UnmountCmd(ipfsDir)
```
