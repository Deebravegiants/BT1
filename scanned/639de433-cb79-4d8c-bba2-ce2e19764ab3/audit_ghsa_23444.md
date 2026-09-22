# [H] Paramiko Unsafe randomness usage may allow access to sensitive information

## Summary
Severity: High
Advisory: GHSA-wqmm-q65g-2hqr
CVE: CVE-2008-0299
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-wqmm-q65g-2hqr
Type: github-advisory

## Affected
- PyPI: `paramiko` — affected >=0 <1.7.1-3

## Details
common.py in Paramiko 1.7.1 and earlier, when using threads or forked processes, does not properly use RandomPool, which allows one session to obtain sensitive information from another session by predicting the state of the pool.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-0299
- https://bugzilla.redhat.com/show_bug.cgi?id=428727
- https://exchange.xforce.ibmcloud.com/vulnerabilities/39749
- https://github.com/paramiko/paramiko
- https://github.com/pypa/advisory-database/tree/main/vulns/paramiko/PYSEC-2008-8.yaml
- https://web.archive.org/web/20080205095439/http://secunia.com/advisories/28488
- https://web.archive.org/web/20080627172450/http://secunia.com/advisories/28510
- https://web.archive.org/web/20080628232710/http://secunia.com/advisories/29168
- https://web.archive.org/web/20080720033315/http://www.lag.net/pipermail/paramiko/2008-January/000599.html
- https://web.archive.org/web/20081012023428/http://www.securityfocus.com/bid/27307
- https://www.redhat.com/archives/fedora-package-announce/2008-January/msg00529.html
- https://www.redhat.com/archives/fedora-package-announce/2008-January/msg00594.html
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=460706
- http://people.debian.org/~nion/nmu-diff/paramiko-1.6.4-1_1.6.4-1.1.patch
- http://security.gentoo.org/glsa/glsa-200803-07.xml
