# [H] SaltStack Salt is vulnerable Arbitrary Directory Access

## Summary
Severity: High
Advisory: GHSA-vp49-2g4r-m3x3
CVE: CVE-2020-11652
CWE: CWE-20, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N/E:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vp49-2g4r-m3x3
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2019.2.4
- PyPI: `salt` — affected >=3000 <3000.2

## Details
An issue was discovered in SaltStack Salt before 2019.2.4 and 3000 before 3000.2. The salt-master process ClearFuncs class allows access to some methods that improperly sanitize paths. These methods allow arbitrary directory access to authenticated users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11652
- https://docs.saltstack.com/en/latest/topics/releases/2019.2.4.html
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2020-103.yaml
- https://github.com/saltstack/salt
- https://github.com/saltstack/salt/blob/v3000.2_docs/doc/topics/releases/3000.2.rst
- https://lists.debian.org/debian-lts-announce/2020/05/msg00027.html
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-salt-2vx545AG
- https://usn.ubuntu.com/4459-1
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-11652
- https://www.debian.org/security/2020/dsa-4676
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00070.html
- http://packetstormsecurity.com/files/157560/Saltstack-3000.1-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/157678/SaltStack-Salt-Master-Minion-Unauthenticated-Remote-Code-Execution.html
- http://support.blackberry.com/kb/articleDetail?articleNumber=000063758
- http://www.vmware.com/security/advisories/VMSA-2020-0009.html
