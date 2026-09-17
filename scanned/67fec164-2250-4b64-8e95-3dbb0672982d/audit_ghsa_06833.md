# [M] Steeltoe: TLS private keys written to /tmp with default permissions, never deleted

## Summary
Severity: Medium
Advisory: GHSA-rxrh-4j9h-xgg9
CVE: CVE-2026-50267
CWE: CWE-312, CWE-732
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-rxrh-4j9h-xgg9
Type: github-advisory

## Affected
- NuGet: `Steeltoe.Configuration.Abstractions` — affected >=4.0.0 <4.2.0

## Details
### Summary

When MySQL or PostgreSQL service bindings from `VCAP_SERVICES` include TLS client credentials, the Connectors library writes those credentials to temporary files in `Path.GetTempPath()` using `File.CreateText`. On Linux, `File.CreateText` creates files with mode `0644` (world-readable) under the process umask, and the files are never deleted. The same key material is protected at mode `0400` in `/proc/<pid>/environ`.

### Impact

Any process co-located in the container that runs as a different UID can read the TLS client private key from `/tmp` and use it to impersonate the application when connecting to the backing database over mutual TLS.

### Affected configuration

- Application is deployed on Cloud Foundry or another environment that populates `VCAP_SERVICES` with a MySQL or PostgreSQL service binding that includes `sslKey` credentials.
- A process running as a different UID shares the container's filesystem.

### Mitigations

If an immediate upgrade is not possible, prevent other processes from running in the container under a different UID with access to `/tmp`.

## References
- https://github.com/SteeltoeOSS/security-advisories/security/advisories/GHSA-rxrh-4j9h-xgg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-50267
- https://github.com/SteeltoeOSS/Steeltoe/commit/8dd97cc6c4b184121a4bd1f92f9ac16918433471
- https://github.com/SteeltoeOSS/security-advisories
