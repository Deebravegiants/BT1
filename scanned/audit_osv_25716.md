# [M] W3m: out-of-bounds write in function checktype() in etc.c (incomplete fix for cve-2022-38223)

## Summary
Severity: Medium
Advisory: CVE-2023-4255
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-12-21
Source: https://osv.dev/vulnerability/CVE-2023-4255
Type: osv

## Details
An out-of-bounds write issue has been discovered in the backspace handling of the checkType() function in etc.c within the W3M application. This vulnerability is triggered by supplying a specially crafted HTML file to the w3m binary. Exploitation of this flaw could lead to application crashes, resulting in a denial of service condition.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AULOBQJLXE2KCT5UVQMKGEFL4GFIAOED/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MKFZQUK7FPWWJQYICDZZ4YWIPUPQ2D3R/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TODROGVCWZ435HQIZE6ARQC5LPQLIA5C/
- https://packages.fedoraproject.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4255.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4255
- https://bugzilla.redhat.com/show_bug.cgi?id=2255207
- https://github.com/tats/w3m/issues/268
- https://github.com/tats/w3m/commit/edc602651c506aeeb60544b55534dd1722a340d3
- https://github.com/tats/w3m/pull/273
