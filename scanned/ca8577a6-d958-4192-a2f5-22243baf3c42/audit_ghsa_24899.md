# [M] MoinMoin Multiple unrestricted file upload vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-m2c4-jgmm-fvq3
CVE: CVE-2012-6081
CWE: CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L/E:F (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-m2c4-jgmm-fvq3
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=0 <1.9.6

## Details
Multiple unrestricted file upload vulnerabilities in the (1) twikidraw (`action/twikidraw.py`) and (2) anywikidraw (`action/anywikidraw.py`) actions in MoinMoin before 1.9.6 allow remote authenticated users with write permissions to execute arbitrary code by uploading a file with an executable extension, then accessing it via a direct request to the file in an unspecified directory, as exploited in the wild in July 2012.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6081
- https://bugs.launchpad.net/ubuntu/+source/moin/+bug/1094599
- https://github.com/moinwiki/moin
- https://github.com/pypa/advisory-database/tree/main/vulns/moin/PYSEC-2013-6.yaml
- https://web.archive.org/web/20200228165146/http://www.securityfocus.com/bid/57082
- http://hg.moinmo.in/moin/1.9/rev/7e7e1cbb9d3f
- http://moinmo.in/MoinMoinRelease1.9
- http://moinmo.in/SecurityFixes
- http://ubuntu.com/usn/usn-1680-1
- http://www.debian.org/security/2012/dsa-2593
- http://www.exploit-db.com/exploits/25304
- http://www.openwall.com/lists/oss-security/2012/12/29/6
- http://www.openwall.com/lists/oss-security/2012/12/30/4
