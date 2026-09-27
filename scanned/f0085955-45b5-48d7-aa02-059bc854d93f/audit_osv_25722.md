# [M] Samba: ad dc busy rpc multiple listener dos

## Summary
Severity: Medium
Advisory: CVE-2023-42670
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-42670
Type: osv

## Details
A flaw was found in Samba. It is susceptible to a vulnerability where multiple incompatible RPC listeners can be initiated, causing disruptions in the AD DC service. When Samba's RPC server experiences a high load or unresponsiveness, servers intended for non-AD DC purposes (for example, NT4-emulation "classic DCs") can erroneously start and compete for the same unix domain sockets. This issue leads to partial query responses from the AD DC, causing issues such as "The procedure number is out of range" when using tools like Active Directory Users. This flaw allows an attacker to disrupt AD DC services.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZUMVALLFFDFC53JZMUWA6HPD7HUGAP5I/
- https://www.samba.org/samba/security/CVE-2023-42670.html
- https://access.redhat.com/security/cve/CVE-2023-42670
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42670.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-42670
- https://security.netapp.com/advisory/ntap-20231124-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2241885
- https://bugzilla.samba.org/show_bug.cgi?id=15473
- https://github.com/samba-team/samba
