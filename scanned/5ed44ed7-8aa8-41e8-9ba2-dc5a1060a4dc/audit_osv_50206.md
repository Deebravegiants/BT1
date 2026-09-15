# [H] CVE-2019-9496

## Summary
Severity: High
Advisory: CVE-2019-9496
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-17
Source: https://osv.dev/vulnerability/CVE-2019-9496
Type: osv

## Details
An invalid authentication sequence could result in the hostapd process terminating due to missing state validation steps when processing the SAE confirm message when in hostapd/AP mode. All version of hostapd with SAE support are vulnerable. An attacker may force the hostapd process to terminate, performing a denial of service attack. Both hostapd with SAE support and wpa_supplicant with SAE support prior to and including version 2.7 are affected.

## References
- http://packetstormsecurity.com/files/152914/FreeBSD-Security-Advisory-FreeBSD-SA-19-03.wpa.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TDOZGR3T7FVO5JSZWK2QPR7AOFIEJTIZ/
- https://seclists.org/bugtraq/2019/May/40
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/56OBBOJJSKRTDGEXZOVFSTP4HDSDBLAE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SVMJOFEYBGXZLFF5IOLW67SSOPKFEJP3/
- https://security.FreeBSD.org/advisories/FreeBSD-SA-19:03.wpa.asc
- https://www.synology.com/security/advisory/Synology_SA_19_16
- https://w1.fi/security/2019-3/
