# [M] FreeRDP: Possible double free in kerberos_AcceptSecurityContext

## Summary
Severity: Medium
Advisory: CVE-2026-33995
Aliases: GHSA-mv25-f4p2-5mxx
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-33995
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.24.2, a double-free vulnerability in kerberos_AcceptSecurityContext() and kerberos_InitializeSecurityContextA() (WinPR, winpr/libwinpr/sspi/Kerberos/kerberos.c) can cause a crash in any FreeRDP clients on systems where Kerberos and/or Kerberos U2U is configured (Samba AD member, or krb5 for NFS). The crash is triggered during NLA connection teardown and requires a failed authentication attempt. This issue has been patched in version 3.24.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33995.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-mv25-f4p2-5mxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33995
- https://github.com/FreeRDP/FreeRDP/commit/8078b8af1359055972e4fb2f509f543b69169391
