# [H] Samba: infinite loop in mdssvc rpc service for spotlight

## Summary
Severity: High
Advisory: CVE-2023-34966
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2023-34966
Type: osv

## Details
An infinite loop vulnerability was found in Samba's mdssvc RPC service for Spotlight. When parsing Spotlight mdssvc RPC packets sent by the client, the core unmarshalling function sl_unpack_loop() did not validate a field in the network packet that contains the count of elements in an array-like structure. By passing 0 as the count value, the attacked function will run in an endless loop consuming 100% CPU. This flaw allows an attacker to issue a malformed RPC request, triggering an infinite loop, resulting in a denial of service condition.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BPCSGND7LO467AJGR5DYBGZLTCGTOBCC/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OT74M42E6C36W7PQVY3OS4ZM7DVYB64Z/
- https://www.samba.org/samba/security/CVE-2023-34966
- https://access.redhat.com/errata/RHSA-2023:6667
- https://access.redhat.com/errata/RHSA-2023:7139
- https://access.redhat.com/errata/RHSA-2024:0423
- https://access.redhat.com/errata/RHSA-2024:0580
- https://access.redhat.com/errata/RHSA-2024:4101
- https://access.redhat.com/security/cve/CVE-2023-34966
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34966.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34966
- https://security.netapp.com/advisory/ntap-20230731-0010/
- https://www.debian.org/security/2023/dsa-5477
- https://bugzilla.redhat.com/show_bug.cgi?id=2222793
