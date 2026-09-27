# [M] Samba: out-of-bounds read in winbind auth_crap

## Summary
Severity: Medium
Advisory: CVE-2022-2127
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2022-2127
Type: osv

## Details
An out-of-bounds read vulnerability was found in Samba due to insufficient length checks in winbindd_pam_auth_crap.c. When performing NTLM authentication, the client replies to cryptographic challenges back to the server. These replies have variable lengths, and Winbind fails to check the lan manager response length. When Winbind is used for NTLM authentication, a maliciously crafted request can trigger an out-of-bounds read in Winbind, possibly resulting in a crash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/04/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BPCSGND7LO467AJGR5DYBGZLTCGTOBCC/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OT74M42E6C36W7PQVY3OS4ZM7DVYB64Z/
- https://www.samba.org/samba/security/CVE-2022-2127.html
- https://access.redhat.com/errata/RHSA-2023:6667
- https://access.redhat.com/errata/RHSA-2023:7139
- https://access.redhat.com/errata/RHSA-2024:0423
- https://access.redhat.com/errata/RHSA-2024:0580
- https://access.redhat.com/security/cve/CVE-2022-2127
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2127.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2127
- https://security.netapp.com/advisory/ntap-20230731-0010/
- https://www.debian.org/security/2023/dsa-5477
- https://bugzilla.redhat.com/show_bug.cgi?id=2222791
