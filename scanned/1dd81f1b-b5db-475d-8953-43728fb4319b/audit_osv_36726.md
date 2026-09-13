# [H] MUNGE has a buffer overflow in message unpacking allows key leakage and credential forgery

## Summary
Severity: High
Advisory: CVE-2026-25506
Aliases: GHSA-r9cr-jf4v-75gh
CVSS: 7.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/CVE-2026-25506
Type: osv

## Details
MUNGE is an authentication service for creating and validating user credentials. From 0.5 to 0.5.17, local attacker can exploit a buffer overflow vulnerability in munged (the MUNGE authentication daemon) to leak cryptographic key material from process memory. With the leaked key material, the attacker could forge arbitrary MUNGE credentials to impersonate any user (including root) to services that rely on MUNGE for authentication. The vulnerability allows a buffer overflow by sending a crafted message with an oversized address length field, corrupting munged's internal state and enabling extraction of the MAC subkey used for credential verification. This vulnerability is fixed in 0.5.18.

## References
- http://www.openwall.com/lists/oss-security/2026/02/10/3
- http://www.openwall.com/lists/oss-security/2026/02/17/6
- https://github.com/dun/munge/releases/tag/munge-0.5.18
- https://lists.debian.org/debian-lts-announce/2026/02/msg00015.html
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-25506.json
- https://access.redhat.com/errata/RHSA-2026:16174
- https://access.redhat.com/errata/RHSA-2026:2918
- https://access.redhat.com/errata/RHSA-2026:2923
- https://access.redhat.com/errata/RHSA-2026:2934
- https://access.redhat.com/errata/RHSA-2026:2949
- https://access.redhat.com/errata/RHSA-2026:2954
- https://access.redhat.com/errata/RHSA-2026:3010
- https://access.redhat.com/errata/RHSA-2026:3011
- https://access.redhat.com/errata/RHSA-2026:3012
- https://access.redhat.com/errata/RHSA-2026:3013
- https://access.redhat.com/errata/RHSA-2026:3032
- https://access.redhat.com/errata/RHSA-2026:3033
- https://access.redhat.com/errata/RHSA-2026:3034
- https://access.redhat.com/security/cve/CVE-2026-25506
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25506.json
