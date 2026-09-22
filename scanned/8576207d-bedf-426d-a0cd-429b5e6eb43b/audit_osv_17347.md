# [M] CVE-2020-1472

## Summary
Severity: Medium
Advisory: CVE-2020-1472
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-08-17
Source: https://osv.dev/vulnerability/CVE-2020-1472
Type: osv

## Details
An elevation of privilege vulnerability exists when an attacker establishes a vulnerable Netlogon secure channel connection to a domain controller, using the Netlogon Remote Protocol (MS-NRPC). An attacker who successfully exploited the vulnerability could run a specially crafted application on a device on the network.
To exploit the vulnerability, an unauthenticated attacker would be required to use MS-NRPC to connect to a domain controller to obtain domain administrator access.
Microsoft is addressing the vulnerability in a phased two-part rollout. These updates address the vulnerability by modifying how Netlogon handles the usage of Netlogon secure channels.
For guidelines on how to manage the changes required for this vulnerability and more information on the phased rollout, see  How to manage the changes in Netlogon secure channel connections associated with CVE-2020-1472 (updated September 28, 2020).
When the second phase of Windows updates become available in Q1 2021, customers will be notified via a revision to this security vulnerability. If you wish to be notified when these updates are released, we recommend that you register for the security notifications mailer to be alerted of content changes to this advisory. See Microsoft Technical Security Notifications.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-1472
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00080.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00086.html
- http://packetstormsecurity.com/files/159190/Zerologon-Proof-Of-Concept.html
- http://www.openwall.com/lists/oss-security/2020/09/17/2
- https://lists.debian.org/debian-lts-announce/2020/11/msg00041.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H4OTFBL6YDVFH2TBJFJIE4FMHPJEEJK3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ST6X3A2XXYMGD4INR26DQ4FP4QSM753B/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TAPQQZZAT4TG3XVRTAFV2Y3S7OAHFBUP/
- https://security.gentoo.org/glsa/202012-24
- https://usn.ubuntu.com/4510-1/
- https://usn.ubuntu.com/4510-2/
- https://usn.ubuntu.com/4559-1/
- https://www.kb.cert.org/vuls/id/490028
- https://www.synology.com/security/advisory/Synology_SA_20_21
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1472
- https://www.oracle.com/security-alerts/cpuApr2021.html
- http://packetstormsecurity.com/files/160127/Zerologon-Netlogon-Privilege-Escalation.html
