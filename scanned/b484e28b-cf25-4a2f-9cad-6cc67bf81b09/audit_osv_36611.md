# [H] Apache Answer: Revision API Improper Access Control leads to Information Disclosure

## Summary
Severity: High
Advisory: CVE-2026-24735
Aliases: GHSA-5w5r-8xc6-2xhw, GO-2026-4421
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-24735
Type: osv

## Details
Exposure of Private Personal Information to an Unauthorized Actor vulnerability in Apache Answer.

This issue affects Apache Answer: through 1.7.1.

An unauthenticated API endpoint incorrectly exposes full revision history for deleted content. This allows unauthorized user to retrieve restricted or sensitive information.
Users are recommended to upgrade to version 2.0.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/02/04/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24735.json
- https://lists.apache.org/thread/whxloom7mpxlyt5wzdskflsg5mzdzd60
- https://nvd.nist.gov/vuln/detail/CVE-2026-24735
