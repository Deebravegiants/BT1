# [C] Samba: smbd allows client access to unix domain sockets on the file system as root

## Summary
Severity: Critical
Advisory: CVE-2023-3961
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-3961
Type: osv

## Details
A path traversal vulnerability was identified in Samba when processing client pipe names connecting to Unix domain sockets within a private directory. Samba typically uses this mechanism to connect SMB clients to remote procedure call (RPC) services like SAMR LSA or SPOOLSS, which Samba initiates on demand. However, due to inadequate sanitization of incoming client pipe names, allowing a client to send a pipe name containing Unix directory traversal characters (../). This could result in SMB clients connecting as root to Unix domain sockets outside the private directory. If an attacker or client managed to send a pipe name resolving to an external service using an existing Unix domain socket, it could potentially lead to unauthorized access to the service and consequential adverse events, including compromise or service crashes.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZUMVALLFFDFC53JZMUWA6HPD7HUGAP5I/
- https://www.samba.org/samba/security/CVE-2023-3961.html
- https://access.redhat.com/errata/RHSA-2023:6209
- https://access.redhat.com/errata/RHSA-2023:6744
- https://access.redhat.com/errata/RHSA-2023:7371
- https://access.redhat.com/errata/RHSA-2023:7408
- https://access.redhat.com/errata/RHSA-2023:7464
- https://access.redhat.com/errata/RHSA-2023:7467
- https://access.redhat.com/security/cve/CVE-2023-3961
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3961.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3961
- https://security.netapp.com/advisory/ntap-20231124-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2241881
- https://bugzilla.samba.org/show_bug.cgi?id=15422
