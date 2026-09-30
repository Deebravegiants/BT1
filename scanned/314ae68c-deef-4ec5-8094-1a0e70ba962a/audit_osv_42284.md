# [M] Apache Qpid Proton-J: Unable to govern the maximum number of transfer frames per incoming delivery

## Summary
Severity: Medium
Advisory: CVE-2026-66277
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-66277
Type: osv

## Details
It was not possible to govern the maximum number of transfer frames per incoming delivery, enabling an authenticated attacker to cause excessive resource usage and potential denial of service.

This issue affects Apache Qpid Proton-J: through 0.34.1.

Users are recommended to upgrade to version 0.35.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/04/13
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66277.json
- https://lists.apache.org/thread/48tflr3sx0sxq9bcdy5rh06oy3gmwx02
- https://nvd.nist.gov/vuln/detail/CVE-2026-66277
