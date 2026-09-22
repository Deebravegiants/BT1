# [M] Apache Qpid Proton-J: Unbounded disposition range handling can lead to denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-66276
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-66276
Type: osv

## Details
An authenticated attacker can craft a disposition frame with large or illegal ranges causing excessive CPU usage due to naive range handling, leading to denial of service.

This issue affects Apache Qpid Proton-J: through 0.34.1.

Users are recommended to upgrade to version 0.35.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/04/12
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66276.json
- https://lists.apache.org/thread/14nj0lpsqpnd3q0hw0t0tw44qvdo1jc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-66276
