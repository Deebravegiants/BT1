# [H] pyftpdlib Use of Insufficiently Random Values of port selection on PASV command

## Summary
Severity: High
Advisory: GHSA-gh7c-cg3x-pmcr
CVE: CVE-2007-6738
CWE: CWE-330
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-gh7c-cg3x-pmcr
Type: github-advisory

## Affected
- PyPI: `pyftpdlib` — affected >=0 <0.1.1

## Details
pyftpdlib before 0.1.1 does not choose a random value for the port associated with the PASV command, which makes it easier for remote attackers to obtain potentially sensitive information about the number of in-progress data connections by reading the response to this command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6738
- https://github.com/giampaolo/pyftpdlib/commit/d171bdc4ef7ac769671946a8a3e5eaafc39a9202
- https://github.com/giampaolo/pyftpdlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyftpdlib/PYSEC-2010-22.yaml
- http://code.google.com/p/pyftpdlib/source/browse/trunk/HISTORY
