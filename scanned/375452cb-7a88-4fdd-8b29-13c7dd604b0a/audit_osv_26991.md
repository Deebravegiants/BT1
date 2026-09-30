# [M] Sudo: improper handling of ipa_hostname leads to privilege mismanagement

## Summary
Severity: Medium
Advisory: CVE-2023-7090
CVSS: 6.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2023-12-23
Source: https://osv.dev/vulnerability/CVE-2023-7090
Type: osv

## Details
A flaw was found in sudo in the handling of ipa_hostname, where ipa_hostname from /etc/sssd/sssd.conf was not propagated in sudo. Therefore, it leads to privilege mismanagement vulnerability in applications, where client hosts retain privileges even after retracting them.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/02/msg00002.html
- https://packages.fedoraproject.org/
- https://www.sudo.ws/releases/legacy/#1.8.28
- https://access.redhat.com/security/cve/CVE-2023-7090
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/7xxx/CVE-2023-7090.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-7090
- https://security.netapp.com/advisory/ntap-20240208-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2255723
