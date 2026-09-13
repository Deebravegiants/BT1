# [H] Cobbler Web Interface Kickstart Template Remote Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: GHSA-p8w2-f44p-fmcj
CVE: CVE-2008-6954
CWE: CWE-94
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p8w2-f44p-fmcj
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0 <1.2.9

## Details
The web interface (CobblerWeb) in Cobbler before 1.2.9 allows remote authenticated users to execute arbitrary Python code with the root privileges in cobblerd by editing a Cheetah kickstart template to import arbitrary Python modules.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-6954
- https://exchange.xforce.ibmcloud.com/vulnerabilities/46625
- https://github.com/cobbler/cobbler
- https://web.archive.org/web/20111227125913/http://secunia.com/advisories/32804
- https://web.archive.org/web/20111227151912/http://secunia.com/advisories/32737
- https://web.archive.org/web/20200228143518/http://www.securityfocus.com/bid/32317
- https://www.redhat.com/archives/fedora-package-announce/2008-November/msg00462.html
- https://www.redhat.com/archives/fedora-package-announce/2008-November/msg00485.html
- http://freshmeat.net/projects/cobbler/releases/288374
