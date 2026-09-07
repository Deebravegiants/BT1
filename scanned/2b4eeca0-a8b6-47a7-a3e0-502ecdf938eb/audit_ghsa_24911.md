# [M] pyrad uses sequential packet IDs

## Summary
Severity: Medium
Advisory: GHSA-w4px-9pgm-p2f3
CVE: CVE-2013-0342
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-w4px-9pgm-p2f3
Type: github-advisory

## Affected
- PyPI: `pyrad` — affected >=0 <2.1

## Details
The CreateID function in packet.py in pyrad before 2.1 uses sequential packet IDs, which makes it easier for remote attackers to spoof packets by predicting the next ID, a different vulnerability than CVE-2013-0294.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0342
- https://github.com/pyradius/pyrad/commit/38f74b36814ca5b1a27d9898141126af4953bee5
- https://bugzilla.redhat.com/show_bug.cgi?id=911685
- https://exchange.xforce.ibmcloud.com/vulnerabilities/82134
- https://github.com/pypa/advisory-database/tree/main/vulns/pyrad/PYSEC-2019-154.yaml
- https://github.com/pyradius/pyrad
- https://web.archive.org/web/20200302193833/http://www.securityfocus.com/bid/57984
- http://www.openwall.com/lists/oss-security/2013/02/15/9
- http://www.openwall.com/lists/oss-security/2013/02/21/27
- http://www.openwall.com/lists/oss-security/2013/02/22/2
