# [H] Docker: `PUT /containers/{id}/archive` executes container binary on the host

## Summary
Severity: High
Advisory: GHSA-x86f-5xw2-fm2r
CVE: CVE-2026-41567
CWE: CWE-427
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-x86f-5xw2-fm2r
Type: github-advisory

## Affected
- Go: `github.com/moby/moby/v2` — affected >=0 <2.0.0-beta.14
- Go: `github.com/docker/docker` — affected >=0
- Go: `github.com/moby/moby` — affected >=0

## Details
## Summary

When a user uploads a compressed archive into a container, a malicious image can execute arbitrary code with daemon (host root) privileges.

## Details

When handling `PUT /containers/{id}/archive` requests with compressed archives, the daemon decompresses them using external system binaries. Due to incorrect ordering of operations, these binaries are resolved from the container's filesystem rather than the host's. A container image that includes a trojanized decompression binary can achieve code execution as the daemon process whenever a compressed archive is uploaded to that container.

The executed binary runs with the daemon's full privileges, including host root UID and unrestricted capabilities.

## Impact

Arbitrary code execution as host root, crossing the container-to-host trust boundary.

### Conditions for exploitation

- A user must run a container from a malicious image that contains a trojanized decompression binary.
- The user must then upload a compressed archive (xz or gzip) into that container, either by piping a compressed archive via `docker cp -` or by calling the `PUT /containers/{id}/archive` API directly with compressed content.

### Not affected

Standard `docker cp` usage is **not** affected, because the CLI sends uncompressed tar by default:

```
docker cp ./file.txt mycontainer:/file.txt
```

This can only be exploited when explicitly passing a xz or gzip-compressed archive to `docker cp` or the `PUT /containers/{id}/archive` API, for example:

```
cat archive.tar.xz | docker cp - mycontainer:/dir
```

Decompression formats using pure Go implementations (bzip2, zstd, and gzip when the container image does not contain an `unpigz` binary) are also not affected.

## Workarounds

- Only run containers from trusted images.
- Use authorization plugins to limit access to the `PUT /containers/{id}/archive` endpoint.
- Avoid piping compressed archives into containers created from untrusted images.

## References
- https://github.com/moby/moby/security/advisories/GHSA-x86f-5xw2-fm2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41567
- https://github.com/moby/moby
