# [H] InstructLab vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-pqmg-c2j8-fq92
CVE: CVE-2026-6855
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-pqmg-c2j8-fq92
Type: github-advisory

## Affected
- PyPI: `instructlab` — affected >=0

## Details
A flaw was found in InstructLab. A local attacker could exploit a path traversal vulnerability in the chat session handler by manipulating the `logs_dir` parameter. This allows the attacker to create new directories and write files to arbitrary locations on the system, potentially leading to unauthorized data modification or disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6855
- https://access.redhat.com/security/cve/CVE-2026-6855
- https://bugzilla.redhat.com/show_bug.cgi?id=2460013
- https://github.com/instructlab/instructlab
