# [M] Samba: spotlight server-side share path disclosure

## Summary
Severity: Medium
Advisory: CVE-2023-34968
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2023-34968
Type: osv

## Details
A path disclosure vulnerability was found in Samba. As part of the Spotlight protocol, Samba discloses the server-side absolute path of shares, files, and directories in the results for search queries. This flaw allows a malicious client or an attacker with a targeted RPC request to view the information that is part of the disclosed path.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BPCSGND7LO467AJGR5DYBGZLTCGTOBCC/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OT74M42E6C36W7PQVY3OS4ZM7DVYB64Z/
- https://www.samba.org/samba/security/CVE-2023-34968.html
- https://access.redhat.com/errata/RHSA-2023:6667
- https://access.redhat.com/errata/RHSA-2023:7139
- https://access.redhat.com/errata/RHSA-2024:0423
- https://access.redhat.com/errata/RHSA-2024:0580
- https://access.redhat.com/security/cve/CVE-2023-34968
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34968.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34968
- https://security.netapp.com/advisory/ntap-20230731-0010/
- https://www.debian.org/security/2023/dsa-5477
- https://bugzilla.redhat.com/show_bug.cgi?id=2222795
