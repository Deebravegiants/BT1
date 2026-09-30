# [M] AIDE null pointer dereference when reading incorrectly encoded xattr attributes from database (local DoS)

## Summary
Severity: Medium
Advisory: CVE-2025-54409
Aliases: GHSA-79g7-f8rv-jcxh
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-14
Source: https://osv.dev/vulnerability/CVE-2025-54409
Type: osv

## Details
AIDE is an advanced intrusion detection environment. From versions 0.13 to 0.19.1, there is a null pointer dereference vulnerability in AIDE. An attacker can crash the program during report printing or database listing after setting extended file attributes with an empty attribute value or with a key containing a comma. A local user might exploit this to cause a local denial of service. This issue has been patched in version 0.19.2. A workaround involves removing xattrs group from rules matching files on affected file systems.

## References
- http://www.openwall.com/lists/oss-security/2025/08/14/8
- https://github.com/aide/aide/releases/tag/v0.19.2
- https://lists.debian.org/debian-lts-announce/2025/08/msg00011.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54409.json
- https://github.com/aide/aide/security/advisories/GHSA-79g7-f8rv-jcxh
- https://nvd.nist.gov/vuln/detail/CVE-2025-54409
- https://github.com/aide/aide/commit/54a6d0d9d5f14b81961d66373c0291bf4af4135a
