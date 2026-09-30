# [?] address review remarks. added vulnerability checks

## Summary
Severity: Unknown
Chain: Mina
Component: MinaProtocol/mina
Published: 2025-12-12
Source: https://github.com/MinaProtocol/mina/commit/2cb0549d3f239c90201043ef435627e80aab7446
Type: security-commit

## Details
address review remarks. added vulnerability checks

## Patch
### scripts/debian/session/deb-session-common.sh
```diff
@@ -0,0 +1,48 @@
+#!/usr/bin/env bash
+
+# Common functions for Debian package session scripts
+# This library provides shared utilities for session validation and security checks.
+
+# Validates that a session directory exists and has the correct structure
+# Usage: validate_session_dir <session-dir-abs-path>
+# Exits with code 1 if validation fails
+validate_session_dir() {
+  local session_dir_abs="$1"
+
+  if [[ ! -d "$session_dir_abs/data" ]]; then
+    echo "ERROR: Session data directory not found. Invalid session?" >&2
+    exit 1
+  fi
+}
+
+# Validates that a path doesn't contain '..' to prevent directory traversal attacks
+# Usage: validate_path_no_traversal <path> [<path-description>]
+# Exits with code 1 if validation fails
+validate_path_no_traversal() {
+  local path="$1"
+  local description="${2:-Path}"
+
+  if [[ "$path" == *".."* ]]; then
+    echo "ERROR: $description contains '..' which is not allowed for security reasons" >&2
+    exit 1
+  fi
+}
+
+# Validates that a tar archive doesn't contain paths with '..' to prevent directory traversal
+# Usage: validate_tar_archive <tar-file>
+# Exits with code 1 if validation fails
+validate_tar_archive() {
+  local tar_file="$1"
+
+  if tar -tf "$tar_file" | grep -q '\.\.'; then
+    echo "ERROR: Archive contains paths with '..' which is a security risk" >&2
+    exit 1
+  fi
+}
+
+# Strips the leading slash from a path
+# Usage: result=$(strip_leading_slash <path>)
+strip_leading_slash() {
+  local path="$1"
+  echo "${path#/}"
+}
```

### scripts/debian/session/deb-session-insert.sh
```diff
@@ -2,6 +2,10 @@
 
 set -euox pipefail
 
+# Source common functions
+SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
+source "$SCRIPT_DIR/deb-session-common.sh"
+
 usage() {
   cat <<EOF
 Usage: $0 <session-dir> <dest-path> <source-file> [<source-file2> ...]
@@ -51,10 +55,10 @@ fi
 SESSION_DIR_ABS=$(readlink -f "$SESSION_DIR")
 
 # Validate session
-if [[ ! -d "$SESSION_DIR_ABS/data" ]]; then
-  echo "ERROR: Session data directory not found. Invalid session?" >&2
-  exit 1
-fi
+validate_session_dir "$SESSION_DIR_ABS"
+
+# Validate destination path for directory traversal
+validate_path_no_traversal "$DEST_PATH" "Destination path"
 
 # Resolve source files to absolute paths and validate
 SOURCE_FILES_ABS=()
@@ -72,9 +76,9 @@ if [[ ${#SOURCE_FILES_ABS[@]} -eq 0 ]]; then
 fi
 
 # Determine if destination is a directory or file
-IS_DIR=false
+DEST_IS_DIR=false
 if [[ "$DEST_PATH" == */ ]]; then
-  IS_DIR=true
+  DEST_IS_DIR=true
 else
   # If not ending with /, check if we have only one source file
   if [[ ${#SOURCE_FILES_ABS[@]} -ne 1 ]]; then
@@ -90,7 +94,7 @@ echo "Destination: $DEST_PATH"
 echo "Files to insert: ${#SOURCE_FILES_ABS[@]}"
 
 # Strip leading slash
-DEST_PATH_STRIPPED="${DEST_PATH#/}"
+DEST_PATH_STRIPPED=$(strip_leading_slash "$DEST_PATH")
 
 cd "$SESSION_DIR_ABS/data"
 
@@ -99,7 +103,7 @@ INSERTED_COUNT=0
 for SOURCE_FILE in "${SOURCE_FILES_ABS[@]}"; do
   SOURCE_BASENAME=$(basename "$SOURCE_FILE")
 
-  if [[ "$IS_DIR" == true ]]; then
+  if [[ "$DEST_IS_DIR" == true ]]; then
     # Destination is a directory
     TARGET_PATH="${DEST_PATH_STRIPPED}${SOURCE_BASENAME}"
   else
```

### scripts/debian/session/deb-session-move.sh
```diff
@@ -2,6 +2,10 @@
 
 set -euox pipefail
 
+# Source common functions
+SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
+source "$SCRIPT_DIR/deb-session-common.sh"
+
 usage() {
   cat <<EOF
 Usage: $0 <session-dir> <source-path> <dest-path>
@@ -46,14 +50,15 @@ fi
 SESSION_DIR_ABS=$(readlink -f "$SESSION_DIR")
 
 # Validate session
-if [[ ! -d "$SESSION_DIR_ABS/data" ]]; then
-  echo "ERROR: Session data directory not found. Invalid session?" >&2
-  exit 1
-fi
+validate_session_dir "$SESSION_DIR_ABS"
+
+# Validate paths for directory traversal
+validate_path_no_traversal "$SOURCE_PATH" "Source path"
+validate_path_no_traversal "$DEST_PATH" "Destination path"
 
 # Strip leading slashes
-SOURCE_PATH_STRIPPED="${SOURCE_PATH#/}"
-DEST_PATH_STRIPPED="${DEST_PATH#/}"
+SOURCE_PATH_STRIPPED=$(strip_leading_slash "$SOURCE_PATH")
+DEST_PATH_STRIPPED=$(strip_leading_slash "$DEST_PATH")
 
 echo "=== Moving File in Package ==="
 echo "Session: $SESSION_DIR_ABS"
```

### scripts/debian/session/deb-session-open.sh
```diff
@@ -2,6 +2,10 @@
 
 set -euox pipefail
 
+# Source common functions
+SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
+source "$SCRIPT_DIR/deb-session-common.sh"
+
 usage() {
   cat <<EOF
 Usage: $0 <input.deb> <session-dir>
@@ -50,6 +54,11 @@ INPUT_DEB_ABS=$(readlink -f "$INPUT_DEB")
 
 # Create or clean session directory
 if [[ -d "$SESSION_DIR" ]]; then
+  # Security: Prevent SESSION_DIR from being a symlink to prevent escaping workspace
+  if [[ -L "$SESSION_DIR" ]]; then
+    echo "ERROR: Session directory cannot be a symlink (security restriction)" >&2
+    exit 1
+  fi
   echo "Cleaning existing session directory: $SESSION_DIR"
   rm -rf "$SESSION_DIR"/*
 else
@@ -107,30 +116,33 @@ esac
 # Extract control.tar.* into control/
 mkdir -p control
 echo "Extracting control archive..."
+validate_tar_archive "$CONTROL_TAR"
 tar -xf "$CONTROL_TAR" -C control
 
 # Extract data.tar.* into data/
 mkdir -p data
 echo "Extracting data archive..."
+validate_tar_archive "$DATA_TAR"
 tar -xf "$DATA_TAR" -C data
 
 # Create metadata file
 echo "Creating session metadata..."
-cat > metadata.env <<METADATA
-# Debian Package Session Metadata
-# Generated by deb-session-open.sh
-
-INPUT_DEB="$INPUT_DEB_ABS"
-SESSION_DIR="$SESSION_DIR_ABS"
-DATA_COMPRESS="$DATA_COMPRESS"
-CONTROL_COMPRESS="$CONTROL_COMPRESS"
-CREATED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
-
-# Original package info
-PACKAGE_NAME="$(dpkg-deb --field "$INPUT_DEB_ABS" Package || echo "unknown")"
-PACKAGE_VERSION="$(dpkg-deb --field "$INPUT_DEB_ABS" Version || echo "unknown")"
-PACKAGE_ARCH="$(dpkg-deb --field "$INPUT_DEB_ABS" Architecture || echo "unknown")"
-METADATA
+# Security: Use printf '%q' to safely escape values to prevent command injection
+{
+  echo "# Debian Package Session Metadata"
+  echo "# Generated by deb-session-open.sh"
+  echo ""
+  printf "INPUT_DEB=%q\n" "$INPUT_DEB_ABS"
+  printf "SESSION_DIR=%q\n" "$SESSION_DIR_ABS"
+  printf "DATA_COMPRESS=%q\n" "$DATA_COMPRESS"
+  printf "CONTROL_COMPRESS=%q\n" "$CONTROL_COMPRESS"
+  printf "CREATED_AT=%q\n" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
+  echo ""
+  echo "# Original package info"
+  printf "PACKAGE_NAME=%q\n" "$(dpkg-deb --field "$INPUT_DEB_ABS" Package || echo "unknown")"
+  printf "PACKAGE_VERSION=%q\n" "$(dpkg-deb --field "$INPUT_DEB_ABS" Version || echo "unknown")"
+  printf "PACKAGE_ARCH=%q\n" "$(dpkg-deb --field "$INPUT_DEB_ABS" Architecture || echo "unknown")"
+} > metadata.env
 
 # Clean up the extracted tar files (we only need the unpacked directories)
 rm -f "$CONTROL_TAR" "$DATA_TAR"
```

### scripts/debian/session/deb-session-remove.sh
```diff
@@ -2,6 +2,10 @@
 
 set -euox pipefail
 
+# Source common functions
+SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
+source "$SCRIPT_DIR/deb-session-common.sh"
+
 usage() {
   cat <<EOF
 Usage: $0 <session-dir> <path-pattern>
@@ -51,13 +55,13 @@ fi
 SESSION_DIR_ABS=$(readlink -f "$SESSION_DIR")
 
 # Validate session
-if [[ ! -d "$SESSION_DIR_ABS/data" ]]; then
-  echo "ERROR: Session data directory not found. Invalid session?" >&2
-  exit 1
-fi
+validate_session_dir "$SESSION_DIR_ABS"
+
+# Validate path pattern for directory traversal
+validate_path_no_traversal "$PATH_PATTERN" "Path pattern"
 
 # Strip leading slash for path inside data/
-PATH_PATTERN_STRIPPED="${PATH_PATTERN#/}"
+PATH_PATTERN_STRIPPED=$(strip_leading_slash "$PATH_PATTERN")
 
 echo "=== Removing File(s) from Package ==="
 echo "Session: $SESSION_DIR_ABS"
@@ -67,6 +71,7 @@ cd "$SESSION_DIR_ABS/data"
 
 # Find matching files
 MATCHED_FILES=()
+# NOTE: globstar requires Bash 4.0+. The ** pattern allows matching files recursively.
 shopt -s globstar nullglob
 if [[ "$PATH_PATTERN_STRIPPED" == *"*"* ]] || [[ "$PATH_PATTERN_STRIPPED" == *"?"* ]]; then
   # Glob pattern - find all matching files
```

### scripts/debian/session/deb-session-rename-package.sh
```diff
@@ -83,7 +83,7 @@ if [[ "$OLD_PACKAGE_NAME" == "$NEW_PACKAGE_NAME" ]]; then
 fi
 
 # Update the Package field
-sed -i "s/^Package: .*/Package: $NEW_PACKAGE_NAME/" "$CONTROL_FILE"
+sed -i "s/^Package: .*$/Package: $NEW_PACKAGE_NAME/" "$CONTROL_FILE"
 
 # Verify the change
 UPDATED_PACKAGE_NAME=$(grep '^Package:' "$CONTROL_FILE" | awk '{print $2}' || true)
```

### scripts/debian/session/deb-session-replace.sh
```diff
@@ -2,6 +2,10 @@
 
 set -euox pipefail
 
+# Source common functions
+SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
+source "$SCRIPT_DIR/deb-session-common.sh"
+
 usage() {
   cat <<EOF
 Usage: $0 <session-dir> <path-in-package> <replacement-file>
@@ -53,13 +57,13 @@ fi
 REPLACEMENT_ABS=$(readlink -f "$REPLACEMENT")
 
 # Validate session
-if [[ ! -d "$SESSION_DIR_ABS/data" ]]; then
-  echo "ERROR: Session data directory not found. Invalid session?" >&2
-  exit 1
-fi
+validate_session_dir "$SESSION_DIR_ABS"
+
+# Validate path for directory traversal
+validate_path_no_traversal "$PKG_PATH" "Package path"
 
 # Strip leading slash for path inside data/
-PKG_PATH_STRIPPED="${PKG_PATH#/}"
+PKG_PATH_STRIPPED=$(strip_leading_slash "$PKG_PATH")
 
 echo "=== Replacing File(s) in Package ==="
 echo "Session: $SESSION_DIR_ABS"
```
