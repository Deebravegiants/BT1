# [M] MoinMoin Multiple cross-site scripting (XSS) vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-7hjm-hqgj-xv9f
CVE: CVE-2009-0260
CWE: CWE-79
Ecosystem: PyPI
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-7hjm-hqgj-xv9f
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=0 <1.8.1

## Details
Multiple cross-site scripting (XSS) vulnerabilities in `action/AttachFile.py` in MoinMoin before 1.8.1 allow remote attackers to inject arbitrary web script or HTML via an AttachFile action to the WikiSandBox component with (1) the rename parameter or (2) the drawing parameter (aka the basename variable).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0260
- https://exchange.xforce.ibmcloud.com/vulnerabilities/48126
- https://usn.ubuntu.com/716-1
- https://web.archive.org/web/20200228171520/http://hg.moinmo.in/moin/1.8/rev/8cb4d34ccbc1
- https://www.debian.org/security/2009/dsa-1715
- http://moinmo.in/SecurityFixes#moin1.8.1
- http://osvdb.org/51485
- http://secunia.com/advisories/33593
- http://secunia.com/advisories/33716
- http://secunia.com/advisories/33755
- http://www.securityfocus.com/archive/1/500197/100/0/threaded
- http://www.securityfocus.com/bid/33365
- http://www.vupen.com/english/advisories/2009/0195
