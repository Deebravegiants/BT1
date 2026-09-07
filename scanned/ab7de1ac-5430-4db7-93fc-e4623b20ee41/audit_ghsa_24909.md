# [C] Ansible Code Injection Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-66c7-5pwv-mm3j
CVE: CVE-2014-4678
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-66c7-5pwv-mm3j
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <1.6.4

## Details
The safe_eval function in Ansible before 1.6.4 does not properly restrict the code subset, which allows remote attackers to execute arbitrary code via crafted instructions. NOTE: this vulnerability exists because of an incomplete fix for CVE-2014-4657.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4678
- https://github.com/ansible/ansible/commit/5429b85b9f6c2e640074176f36ff05fd5e4d1916
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-203.yaml
- https://groups.google.com/forum/message/raw?msg=ansible-announce/ieV1vZvcTXU/5Q93ThkY9rIJ
- https://security-tracker.debian.org/tracker/CVE-2014-4678
- https://www.openwall.com/lists/oss-security/2014/06/26/30
- https://www.openwall.com/lists/oss-security/2014/07/02/2
- https://www.rapid7.com/db/vulnerabilities/freebsd-vid-2c493ac8-205e-11e5-a4a5-002590263bf5
- https://www.rapid7.com/db/vulnerabilities/gentoo-linux-cve-2014-4678
