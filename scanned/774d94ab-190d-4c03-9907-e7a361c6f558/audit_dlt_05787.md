# [?] fix(log): fix panic when log with nil val (#3145)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-06-07
Source: https://github.com/cometbft/cometbft/commit/b13c703f235753d38a5e65b2bc831916925a3d89
Type: security-commit

## Details
fix(log): fix panic when log with nil val (#3145)

replace `Stringer.String` with `fmt.Sprintf` to for log val stringer

<!--

Please add a reference to the issue that this PR addresses and indicate
which
files are most critical to review. If it fully addresses a particular
issue,
please include "Closes #XXX" (where "XXX" is the issue number).

If this PR is non-trivial/large/complex, please ensure that you have
either
created an issue that the team's had a chance to respond to, or had some
discussion with the team prior to submitting substantial pull requests.
The team
can be reached via GitHub Discussions or the Cosmos Network Discord
server in
the #cometbft channel. GitHub Discussions is preferred over Discord as
it
allows us to keep track of conversations topically.
https://github.com/cometbft/cometbft/discussions

If the work in this PR is not aligned with the team's current
priorities, please
be advised that it may take some time before it is merged - especially
if it has
not yet been discussed with the team.

See the project board for the team's current priorities:
https://github.com/orgs/cometbft/projects/1

-->

---

#### PR checklist

- [ ] Tests written/updated
- [ ] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments
- [ ] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec

Co-authored-by: Andy Nogueira <me@andynogueira.dev>
Co-authored-by: Anton Kaliaev <anton.kalyaev@gmail.com>

### .changelog/unreleased/bug-fixes/3145-fix-panic-when-log-with-nil-val.md
```diff
@@ -0,0 +1,3 @@
+- `[log]` Fix panic when log with nil val which is a pointer who implements
+  fmt.Stringer interface
+  ([\#3145](https://github.com/cometbft/cometbft/pull/3145))
```

### libs/log/cmtfmt_logger.go
```diff
@@ -92,7 +92,8 @@ func (l tmfmtLogger) Log(keyvals ...any) error {
 
 		// Realize stringers
 		if s, ok := keyvals[i+1].(fmt.Stringer); ok {
-			keyvals[i+1] = s.String()
+			//nolint:gosimple // avoid panic for nil val
+			keyvals[i+1] = fmt.Sprintf("%s", s)
 		}
 	}
 
```

### libs/log/cmtfmt_logger_test.go
```diff
@@ -2,6 +2,7 @@ package log_test
 
 import (
 	"bytes"
+	"encoding/hex"
 	"errors"
 	"io"
 	"math"
@@ -58,6 +59,26 @@ func TestTMFmtLogger(t *testing.T) {
 		t.Fatal(err)
 	}
 	assert.Regexp(t, regexp.MustCompile(`N\[.+\] unknown \s+ hash=74657374206D65\n$`), buf.String())
+
+	buf.Reset()
+	if err := logger.Log("myhash_obj", myhash("test me")); err != nil {
+		t.Fatal(err)
+	}
+	assert.Regexp(t, regexp.MustCompile(`N\[.+\] unknown \s+ myhash_obj=0x74657374206d65\n$`), buf.String())
+
+	var h *myhash
+	buf.Reset()
+	if err := logger.Log("myhash_nil", h); err != nil {
+		t.Fatal(err)
+	}
+	assert.Regexp(t, regexp.MustCompile(`N\[.+\] unknown \s+ myhash_nil=<nil>\n$`), buf.String())
+
+	h = &myhash{'t', 'e', 's', 't', ' ', 'm', 'e'}
+	buf.Reset()
+	if err := logger.Log("myhash_ptr", h); err != nil {
+		t.Fatal(err)
+	}
+	assert.Regexp(t, regexp.MustCompile(`N\[.+\] unknown \s+ myhash_ptr=0x74657374206d65\n$`), buf.String())
 }
 
 func BenchmarkTMFmtLoggerSimple(b *testing.B) {
@@ -123,3 +144,9 @@ func spam(logger kitlog.Logger, count int) error {
 type mymap map[int]int
 
 func (mymap) String() string { return "special_behavior" }
+
+type myhash []byte
+
+func (h myhash) String() string {
+	return "0x" + hex.EncodeToString(h)
+}
```
