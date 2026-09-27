# [M] Libssh: improper sanitation of paths received from scp servers

## Summary
Severity: Medium
Advisory: CVE-2026-0964
CVSS: 5.0 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-0964
Type: osv

## Details
A malicious SCP server can send unexpected paths that could make the
client application override local files outside of working directory.
This could be misused to create malicious executable or configuration
files and make the user execute them under specific consequences.

This is the same issue as in OpenSSH, tracked as CVE-2019-6111.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://www.libssh.org/2026/02/10/libssh-0-12-0-and-0-11-4-security-releases/
- https://access.redhat.com/errata/RHSA-2026:18160
- https://access.redhat.com/errata/RHSA-2026:18683
- https://access.redhat.com/security/cve/CVE-2026-0964
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0964.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0964
- https://bugzilla.redhat.com/show_bug.cgi?id=2436979
