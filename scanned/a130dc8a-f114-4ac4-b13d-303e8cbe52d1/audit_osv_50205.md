# [M] CVE-2019-9494

## Summary
Severity: Medium
Advisory: CVE-2019-9494
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-17
Source: https://osv.dev/vulnerability/CVE-2019-9494
Type: osv

## Details
The implementations of SAE in hostapd and wpa_supplicant are vulnerable to side channel attacks as a result of observable timing differences and cache access patterns. An attacker may be able to gain leaked information from a side channel attack that can be used for full password recovery. Both hostapd with SAE support and wpa_supplicant with SAE support prior to and including version 2.7 are affected.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TDOZGR3T7FVO5JSZWK2QPR7AOFIEJTIZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/56OBBOJJSKRTDGEXZOVFSTP4HDSDBLAE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SVMJOFEYBGXZLFF5IOLW67SSOPKFEJP3/
- https://security.FreeBSD.org/advisories/FreeBSD-SA-19:03.wpa.asc
- https://www.synology.com/security/advisory/Synology_SA_19_16
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00021.html
- http://packetstormsecurity.com/files/152914/FreeBSD-Security-Advisory-FreeBSD-SA-19-03.wpa.html
- https://seclists.org/bugtraq/2019/May/40
- https://w1.fi/security/2019-1/
