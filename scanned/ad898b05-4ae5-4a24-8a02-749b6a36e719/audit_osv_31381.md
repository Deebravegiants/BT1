# [M] Samba: smbd doesn't pick up group membership changes when re-authenticating an expired smb session

## Summary
Severity: Medium
Advisory: CVE-2025-0620
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-06-06
Source: https://osv.dev/vulnerability/CVE-2025-0620
Type: osv

## Details
A flaw was found in Samba. The smbd service daemon does not pick up group membership changes when re-authenticating an expired SMB session. This issue can expose file shares until clients disconnect and then connect again.

## References
- http://www.openwall.com/lists/oss-security/2025/06/03/8
- https://access.redhat.com/downloads/content/package-browser/
- https://www.samba.org/
- https://www.samba.org/samba/security/CVE-2025-0620.html
- https://access.redhat.com/security/cve/CVE-2025-0620
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0620.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0620
- https://bugzilla.redhat.com/show_bug.cgi?id=2370453
