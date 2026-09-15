# [M] Quill has unbounded memory allocation via unvalidated size fields in Mach-O binary parsing

## Summary
Severity: Medium
Advisory: GHSA-xj69-m9qq-8m94
CVE: CVE-2026-31961
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-xj69-m9qq-8m94
Type: github-advisory

## Affected
- Go: `github.com/anchore/quill` — affected >=0 <0.7.1

## Details
### Impact

Quill before version `v0.7.1` contains an unbounded memory allocation vulnerability when parsing Mach-O binaries. Exploitation requires that Quill processes an attacker-supplied Mach-O binary, which is most likely in environments such as CI/CD pipelines, shared signing services, or any workflow where externally-submitted binaries are accepted for signing.

When parsing a Mach-O binary, Quill reads several size and count fields from the `LC_CODE_SIGNATURE` load command and embedded code signing structures (`SuperBlob`, `BlobIndex`) and uses them to allocate memory buffers without validating that the values are reasonable or consistent with the actual file size. Affected fields include `DataSize`, `DataOffset`, and `Size` from the load command, `Count` from the `SuperBlob` header, and `Length` from individual blob headers. An attacker can craft a minimal (~4KB) malicious Mach-O binary with extremely large values in these fields, causing Quill to attempt to allocate excessive memory. This leads to memory exhaustion and denial of service, potentially crashing the host process. Both the Quill CLI and Go library are affected when used to parse untrusted Mach-O files.


### Patches

Fixed in Quill `v0.7.1`


### Workarounds

None

### Credit

Anchore would like to thank opera-aklajn (Opera) for reporting this vulnerability

### Resources

- [Inside code signing: hashes (Apple documentation)](https://developer.apple.com/documentation/technotes/tn3126-inside-code-signing-hashes)

## References
- https://github.com/anchore/quill/security/advisories/GHSA-xj69-m9qq-8m94
- https://nvd.nist.gov/vuln/detail/CVE-2026-31961
- https://github.com/anchore/quill/commit/80cf3fe082678af0ec4f9f8dd93f39189d2dc1fe
- https://developer.apple.com/documentation/technotes/tn3126-inside-code-signing-hashes
- https://github.com/anchore/quill
- https://github.com/anchore/quill/releases/tag/v0.7.1
