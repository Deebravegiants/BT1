# [H] LibHTP unbounded folded header handling leads to denial service

## Summary
Severity: High
Advisory: CVE-2024-23837
Aliases: GHSA-f9wf-rrjj-qx8m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2024-23837
Type: osv

## Details
LibHTP is a security-aware parser for the HTTP protocol. Crafted traffic can cause excessive processing time of HTTP headers, leading to denial of service. This issue is addressed in 0.5.46.

## References
- https://lists.debian.org/debian-lts-announce/2025/09/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GOCOBFUTIFHOP2PZOH4ENRFXRBHIRKK4/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZXJIT7R53ZXROO3I256RFUWTIW4ECK6P/
- https://redmine.openinfosecfoundation.org/issues/6444
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23837.json
- https://github.com/OISF/libhtp/security/advisories/GHSA-f9wf-rrjj-qx8m
- https://nvd.nist.gov/vuln/detail/CVE-2024-23837
- https://github.com/OISF/libhtp/commit/20ac301d801cdf01b3f021cca08a22a87f477c4a
