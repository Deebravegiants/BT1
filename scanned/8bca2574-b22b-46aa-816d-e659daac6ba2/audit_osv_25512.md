# [M] W3m: out of bounds read in growbuf_to_str() at w3m/indep.c

## Summary
Severity: Medium
Advisory: CVE-2023-38253
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-07-14
Source: https://osv.dev/vulnerability/CVE-2023-38253
Type: osv

## Details
An out-of-bounds read flaw was found in w3m, in the growbuf_to_Str function in indep.c. This issue may allow an attacker to cause a denial of service through a crafted HTML file.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AULOBQJLXE2KCT5UVQMKGEFL4GFIAOED/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MKFZQUK7FPWWJQYICDZZ4YWIPUPQ2D3R/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TODROGVCWZ435HQIZE6ARQC5LPQLIA5C/
- https://packages.fedoraproject.org/
- https://access.redhat.com/security/cve/CVE-2023-38253
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38253.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-38253
- https://bugzilla.redhat.com/show_bug.cgi?id=2222779
- https://github.com/tats/w3m/issues/271
