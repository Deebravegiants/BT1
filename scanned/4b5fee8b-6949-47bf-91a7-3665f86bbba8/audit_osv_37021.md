# [M] GPAC NHML Demuxer (dmx_nhml.c) Vulnerable to Stack Buffer Overflow

## Summary
Severity: Medium
Advisory: CVE-2026-27821
Aliases: GHSA-q7qh-8r2r-q559
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-27821
Type: osv

## Details
GPAC is an open-source multimedia framework. In versions up to and including 26.02.0, a stack buffer overflow occurs during NHML file parsing in `src/filters/dmx_nhml.c`. The value of the xmlHeaderEnd XML attribute is copied from att->value into szXmlHeaderEnd[1000] using strcpy() without any length validation. If the input exceeds 1000 bytes, it overwrites beyond the stack buffer boundary. Commit 9bd7137fded2db40de61a2cf3045812c8741ec52 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27821.json
- https://github.com/gpac/gpac/security/advisories/GHSA-q7qh-8r2r-q559
- https://nvd.nist.gov/vuln/detail/CVE-2026-27821
- https://github.com/gpac/gpac/commit/9bd7137fded2db40de61a2cf3045812c8741ec52
