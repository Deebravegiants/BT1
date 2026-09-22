# [M] Samba: smb2 packet signing is not enforced when "server signing = required" is set

## Summary
Severity: Medium
Advisory: CVE-2023-3347
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2023-3347
Type: osv

## Details
A vulnerability was found in Samba's SMB2 packet signing mechanism. The SMB2 packet signing is not enforced if an admin configured "server signing = required" or for SMB2 connections to Domain Controllers where SMB2 packet signing is mandatory. This flaw allows an attacker to perform attacks, such as a man-in-the-middle attack, by intercepting the network traffic and modifying the SMB2 messages between client and server, affecting the integrity of the data.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BPCSGND7LO467AJGR5DYBGZLTCGTOBCC/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OT74M42E6C36W7PQVY3OS4ZM7DVYB64Z/
- https://www.samba.org/samba/security/CVE-2023-3347.html
- https://access.redhat.com/errata/RHSA-2023:4325
- https://access.redhat.com/errata/RHSA-2023:4328
- https://access.redhat.com/security/cve/CVE-2023-3347
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3347.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3347
- https://security.netapp.com/advisory/ntap-20230731-0010/
- https://www.debian.org/security/2023/dsa-5477
- https://bugzilla.redhat.com/show_bug.cgi?id=2222792
