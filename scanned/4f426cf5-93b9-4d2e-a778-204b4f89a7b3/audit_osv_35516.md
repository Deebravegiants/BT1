# [M] Libssh: libssh: denial of service via zero-length input in ssh_get_hexa()

## Summary
Severity: Medium
Advisory: CVE-2026-0966
CVSS: 6.5 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-0966
Type: osv

## Details
A flaw was found in libssh. The API function `ssh_get_hexa()` is vulnerable to a denial of service when processing zero-length input. This can be exploited remotely by an attacker during GSSAPI (Generic Security Service Application Program Interface) authentication if the server's logging verbosity is set to `SSH_LOG_PACKET (3)` or higher. Successful exploitation could lead to a self-Denial of Service of the per-connection daemon process.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://www.libssh.org/2026/02/10/libssh-0-12-0-and-0-11-4-security-releases/
- https://access.redhat.com/errata/RHSA-2026:18160
- https://access.redhat.com/errata/RHSA-2026:18683
- https://access.redhat.com/errata/RHSA-2026:7067
- https://access.redhat.com/security/cve/CVE-2026-0966
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0966.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0966
- https://bugzilla.redhat.com/show_bug.cgi?id=2433121
