# [C] SaltStack Salt Unauthenticated Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-pjhf-vpx3-33r3
CVE: CVE-2020-11651
CWE: CWE-20, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pjhf-vpx3-33r3
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2019.2.4
- PyPI: `salt` — affected >=3000 <3000.2

## Details
An issue was discovered in SaltStack Salt before 2019.2.4 and 3000 before 3000.2. The salt-master process ClearFuncs class does not properly validate method calls. This allows a remote user to access some methods without authentication. These methods can be used to retrieve user tokens from the salt master and/or run arbitrary commands on salt minions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11651
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2020-102.yaml
- https://github.com/saltstack/salt
- https://github.com/saltstack/salt/blob/v3000.2_docs/doc/topics/releases/3000.2.rst
- https://lists.debian.org/debian-lts-announce/2020/05/msg00027.html
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-salt-2vx545AG
- https://usn.ubuntu.com/4459-1
- https://www.debian.org/security/2020/dsa-4676
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00070.html
- http://packetstormsecurity.com/files/157560/Saltstack-3000.1-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/157678/SaltStack-Salt-Master-Minion-Unauthenticated-Remote-Code-Execution.html
- http://www.vmware.com/security/advisories/VMSA-2020-0009.html
