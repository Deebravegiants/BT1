# [M] iccDEV: HBO in icAnsiToUtf8()

## Summary
Severity: Medium
Advisory: CVE-2026-34556
Aliases: GHSA-p9wm-xfv4-43qg
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34556
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, there is a heap-buffer-overflow (HBO) in icAnsiToUtf8() in the XML conversion path. The issue is triggered by a crafted ICC profile which causes icAnsiToUtf8(std::string&, char const*) to treat an input buffer as a C-string and call operations that rely on strlen()/null-termination. AddressSanitizer reports an out-of-bounds READ of size 115 past a 114-byte heap allocation, with the failure observed while running the iccToXml tool. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34556.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-p9wm-xfv4-43qg
- https://nvd.nist.gov/vuln/detail/CVE-2026-34556
- https://github.com/InternationalColorConsortium/iccDEV/issues/734
- https://github.com/InternationalColorConsortium/iccDEV/pull/740
