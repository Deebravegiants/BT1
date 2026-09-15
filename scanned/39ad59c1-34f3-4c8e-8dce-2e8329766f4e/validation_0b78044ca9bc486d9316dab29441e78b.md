### Title
Windows log-file sink creates `chainlink_debug.log` with ineffective/overly-permissive access, risking disclosure of sensitive log data to unprivileged local users - (File: core/logger/logger_windows.go)

### Summary
The Chainlink node's disk-logging feature on Windows opens its log file through a custom `winfile://` zap sink that calls `os.OpenFile` with a hardcoded Unix-style mode of `0644`, and relies on `os.Chmod`/directory-mode checks elsewhere (`utils.EnsureDirAndMaxPerms`, `checkFilePermissions`) that are effectively no-ops on Windows. This is the same class of bug as GHSA-82m2-cv7p-4m75/CVE-2024-5321: Unix permission bits do not translate to Windows ACL semantics, so the file/directory ends up inheriting the parent directory's (often broad) ACL instead of the intended owner-only restriction, and non-owning local users can read the log.

### Finding Description
`core/logger/logger_windows.go` registers a custom sink specifically because zap/Go's standard `file://` scheme doesn't handle Windows paths correctly: [1](#0-0) 
It opens the debug log file with `os.OpenFile(u.Path[1:], os.O_WRONLY|os.O_APPEND|os.O_CREATE, 0644)`. On Windows, the Go runtime does not map POSIX permission bits to NTFS ACLs (it only toggles the read-only attribute), so the `0644` argument gives no real owner-restriction — the resulting file's effective access is governed by whatever ACL is inherited from the parent directory (`c.Dir`, configured by the node operator via `Log.File.Dir`, defaulting under `RootDir`).

The intended protection mechanism, `utils.EnsureDirAndMaxPerms`, is invoked from `core/cmd/app.go` to restrict the log directory to `0o700` before the logger is (re)configured: [2](#0-1) 
and `core/utils/files.go`'s `EnsureDirAndMaxPerms`/`EnsureFileMaxPerms` rely on `os.Chmod`/`file.Chmod`: [3](#0-2) [4](#0-3) 
`os.Chmod` on Windows likewise only affects the read-only attribute bit and cannot enforce owner-only NTFS ACLs. The same limitation applies to `checkFilePermissions` in `core/cmd/shell_local.go`, which is meant to protect the `secret`, `cookie`, `.password`, `.env`, `.api` files and the `tls` directory using the same `EnsureDirAndMaxPerms`/`EnsureFilepathMaxPerms` helpers: [5](#0-4) 

Because the debug log (`chainlink_debug.log`) can contain operationally sensitive data (request bodies are only selectively redacted, see `core/web/router.go`'s blacklist-based redaction which is not universal), any BUILTIN\Users-equivalent local account able to read the inherited-ACL log directory can read data that the node operator believed was owner-restricted — directly analogous to the "BUILTIN\\Users may be able to read container logs" root cause in the Kubernetes advisory.

### Impact Explanation
An unprivileged local Windows account (any account with read access to the parent directory's inherited ACL, not the intended "owner-only" chainlink service account) could read the node's debug log file, potentially disclosing sensitive operational information (config paths, internal errors, partially redacted request data, stack traces) that the node operator assumed was protected by the `0700`/`0600` permission scheme used on Linux/macOS. This maps to the "secret redaction" and unprivileged-access categories in scope, since the log-permission control is the safeguard meant to prevent unauthorized local disclosure.

### Likelihood Explanation
Likelihood is moderate: exploitation requires local access to the Windows host running the node (not remote), and the actual exposure depends on the ACL inherited from the parent directory (which, depending on how the node's install/service directory was provisioned, may or may not be broadly readable). This mirrors the "Medium-high CVSS but local-only" profile of the original Kubernetes advisory (`AV:L`).

### Recommendation
- On Windows, replace the reliance on POSIX-style `os.OpenFile`/`os.Chmod` mode bits for the log file and log directory with explicit Windows ACL management (e.g., via `golang.org/x/sys/windows` `SetNamedSecurityInfo`/`SetFileSecurity`, or a library such as `hectane/go-acl`) to grant access only to the account running the chainlink service and Administrators.
- Update `core/logger/logger_windows.go`'s `newWinFileSink` to explicitly set a restrictive ACL immediately after creating the file, rather than relying on the ignored `0644` mode.
- Update `core/utils/files.go` (`EnsureDirAndMaxPerms`, `EnsureFileMaxPerms`, `EnsureFilepathMaxPerms`) and `core/cmd/shell_local.go`'s `checkFilePermissions` to perform an OS-specific ACL check/enforcement on Windows instead of a no-op `os.Chmod`, so that log/secret/cookie/TLS directories are genuinely owner-restricted rather than only nominally so.
- Add a Windows-specific test (analogous to `testdata/scripts/node/validate/disk-based-logging-disabled.txtar`) validating that the log file/directory ACL restricts access to the running service account only.

### Proof of Concept
1. Run the Chainlink node on Windows with disk logging enabled (`Log.File.MaxSize` > 0), causing `newWinFileSink` in `core/logger/logger_windows.go` to create `chainlink_debug.log` via `os.OpenFile(..., 0644)`.
2. Observe that the resulting file/directory ACL is inherited from the parent directory rather than being restricted to the service account, since `0644`/`os.Chmod` calls throughout `core/utils/files.go` and `core/cmd/shell_local.go`'s `checkFilePermissions` are non-functional on Windows for ACL purposes.
3. From a second, unprivileged local Windows account that has read access to the parent directory (e.g., a shared install path or default service directory with inherited "Users" read permission), read `chainlink_debug.log` and confirm it can be opened and its contents viewed, despite the node's intended `0700`/owner-only permission model (as enforced correctly on Linux).

### Citations

**File:** core/logger/logger_windows.go (L21-29)
```go
func registerOSSinks() error {
	return zap.RegisterSink("winfile", newWinFileSink)
}

func newWinFileSink(u *url.URL) (zap.Sink, error) {
	// https://github.com/uber-go/zap/issues/621
	// Remove leading slash left by url.Parse()
	return os.OpenFile(u.Path[1:], os.O_WRONLY|os.O_APPEND|os.O_CREATE, 0644)
}
```

**File:** core/cmd/app.go (L256-262)
```go
				logFileMaxSizeMB := s.Config.Log().File().MaxSize() / utils.MB
				if logFileMaxSizeMB > 0 {
					err = utils.EnsureDirAndMaxPerms(s.Config.Log().File().Dir(), os.FileMode(0o700))
					if err != nil {
						return err
					}
				}
```

**File:** core/utils/files.go (L36-52)
```go
func EnsureDirAndMaxPerms(path string, perms os.FileMode) error {
	stat, err := os.Stat(path)
	if err != nil && !os.IsNotExist(err) {
		// Regular error
		return err
	} else if os.IsNotExist(err) {
		// Dir doesn't exist, create it with desired perms
		return os.MkdirAll(path, perms)
	} else if !stat.IsDir() {
		// Path exists, but it's a file, so don't clobber
		return errors.Errorf("%v already exists and is not a directory", path)
	} else if stat.Mode() != perms {
		// Dir exists, but wrong perms, so chmod
		return os.Chmod(path, stat.Mode()&perms)
	}
	return nil
}
```

**File:** core/utils/files.go (L70-81)
```go
// EnsureFileMaxPerms ensures that the given file has permissions
// that are no more permissive than the given ones.
func EnsureFileMaxPerms(file *os.File, perms os.FileMode) error {
	stat, err := file.Stat()
	if err != nil {
		return err
	}
	if stat.Mode() == perms {
		return nil
	}
	return file.Chmod(stat.Mode() & perms)
}
```

**File:** core/cmd/shell_local.go (L692-748)
```go
func checkFilePermissions(lggr logger.Logger, rootDir string) error {
	// Ensure tls sub directory (and children) permissions are <= `ownerPermsMask``
	tlsDir := filepath.Join(rootDir, "tls")
	if _, err := os.Stat(tlsDir); err != nil && !os.IsNotExist(err) {
		lggr.Errorf("error checking perms of 'tls' directory: %v", err)
	} else if err == nil {
		err := utils.EnsureDirAndMaxPerms(tlsDir, ownerPermsMask)
		if err != nil {
			return fmt.Errorf("failed to ensure TLS directory permissions for %s: %w", tlsDir, err)
		}

		err = filepath.Walk(tlsDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				lggr.Errorf(`error checking perms of "%v": %v`, path, err)
				return fmt.Errorf("error checking permissions of %s: %w", path, err)
			}
			if utils.TooPermissive(info.Mode().Perm(), ownerPermsMask) {
				newPerms := info.Mode().Perm() & ownerPermsMask
				lggr.Warnf("%s has overly permissive file permissions, reducing them from %s to %s", path, info.Mode().Perm(), newPerms)
				return utils.EnsureFilepathMaxPerms(path, newPerms)
			}
			return nil
		})
		if err != nil {
			return fmt.Errorf("failed to walk TLS directory %s: %w", tlsDir, err)
		}
	}

	// Ensure {secret,cookie} files' permissions are <= `ownerPermsMask``
	protectedFiles := []string{"secret", "cookie", ".password", ".env", ".api"}
	for _, fileName := range protectedFiles {
		path := filepath.Join(rootDir, fileName)
		fileInfo, err := os.Stat(path)
		if os.IsNotExist(err) {
			continue
		} else if err != nil {
			return fmt.Errorf("failed to stat file %s: %w", path, err)
		}
		if utils.TooPermissive(fileInfo.Mode().Perm(), ownerPermsMask) {
			newPerms := fileInfo.Mode().Perm() & ownerPermsMask
			lggr.Warnf("%s has overly permissive file permissions, reducing them from %s to %s", path, fileInfo.Mode().Perm(), newPerms)
			err = utils.EnsureFilepathMaxPerms(path, newPerms)
			if err != nil {
				return fmt.Errorf("failed to set permissions for %s: %w", path, err)
			}
		}
		owned, err := utils.IsFileOwnedByChainlink(fileInfo)
		if err != nil {
			lggr.Warn(err)
			continue
		}
		if !owned {
			lggr.Warnf("The file %v is not owned by the user running chainlink. This will be made mandatory in the future.", path)
		}
	}
	return nil
}
```
