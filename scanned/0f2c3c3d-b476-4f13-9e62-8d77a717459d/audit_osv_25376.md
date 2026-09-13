# [M] Samba: type confusion in mdssvc rpc service for spotlight

## Summary
Severity: Medium
Advisory: CVE-2023-34967
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2023-34967
Type: osv

## Details
A Type Confusion vulnerability was found in Samba's mdssvc RPC service for Spotlight. When parsing Spotlight mdssvc RPC packets, one encoded data structure is a key-value style dictionary where the keys are character strings, and the values can be any of the supported types in the mdssvc protocol. Due to a lack of type checking in callers of the dalloc_value_for_key() function, which returns the object associated with a key, a caller may trigger a crash in talloc_get_size() when talloc detects that the passed-in pointer is not a valid talloc pointer. With an RPC worker process shared among multiple client connections, a malicious client or attacker can trigger a process crash in a shared RPC mdssvc worker process, affecting all other clients this worker serves.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BPCSGND7LO467AJGR5DYBGZLTCGTOBCC/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OT74M42E6C36W7PQVY3OS4ZM7DVYB64Z/
- https://www.samba.org/samba/security/CVE-2023-34967.html
- https://access.redhat.com/errata/RHSA-2023:6667
- https://access.redhat.com/errata/RHSA-2023:7139
- https://access.redhat.com/errata/RHSA-2024:0423
- https://access.redhat.com/errata/RHSA-2024:0580
- https://access.redhat.com/security/cve/CVE-2023-34967
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34967.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34967
- https://security.netapp.com/advisory/ntap-20230731-0010/
- https://www.debian.org/security/2023/dsa-5477
- https://bugzilla.redhat.com/show_bug.cgi?id=2222794
