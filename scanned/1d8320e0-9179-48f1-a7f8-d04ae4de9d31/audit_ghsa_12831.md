# [M] Tokio reject_remote_clients configuration may get dropped when creating a Windows named pipe

## Summary
Severity: Medium
Advisory: GHSA-7rrj-xr53-82p7
CVE: CVE-2023-22466
CWE: CWE-665
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-7rrj-xr53-82p7
Type: github-advisory

## Affected
- crates.io: `tokio` — affected >=1.7.0 <1.18.4
- crates.io: `tokio` — affected >=1.19.0 <1.20.3
- crates.io: `tokio` — affected >=1.21.0 <1.23.1

## Details
### Impact

When configuring a Windows named pipe server, setting `pipe_mode` will reset `reject_remote_clients` to `false`. If the application has previously configured `reject_remote_clients` to `true`, this effectively undoes the configuration. This also applies if `reject_remote_clients` is not explicitly set as this is the default configuration and is cleared by calling `pipe_mode`.

Remote clients may only access the named pipe if the named pipe's associated path is accessible via a publically shared folder (SMB).

### Patches

The following versions have been patched:
* 1.23.1
* 1.20.3
* 1.18.4

The fix will also be present in all releases starting from version 1.24.0.

Named pipes were introduced to Tokio in version 1.7.0, so releases older than 1.7.0 are not affected.

### Workarounds

Ensure that `pipe_mode` is set **first** after initializing a `ServerOptions`. For example:

```rust
let mut opts = ServerOptions::new();
opts.pipe_mode(PipeMode::Message);
opts.reject_remote_clients(true);
```

### References

https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea#pipe_reject_remote_clients

## References
- https://github.com/tokio-rs/tokio/security/advisories/GHSA-7rrj-xr53-82p7
- https://nvd.nist.gov/vuln/detail/CVE-2023-22466
- https://github.com/tokio-rs/tokio/pull/5336
- https://github.com/tokio-rs/tokio
- https://github.com/tokio-rs/tokio/releases/tag/tokio-1.23.1
- https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea#pipe_reject_remote_clients
- https://rustsec.org/advisories/RUSTSEC-2023-0001.html
