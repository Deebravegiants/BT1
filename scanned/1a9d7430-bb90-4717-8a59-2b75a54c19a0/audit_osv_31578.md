# [H] Libssh: libssh: insecure default configuration leads to local man-in-the-middle attacks on windows

## Summary
Severity: High
Advisory: CVE-2025-14821
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2025-14821
Type: osv

## Details
A flaw was found in libssh. This vulnerability allows local man-in-the-middle attacks, security downgrades of SSH (Secure Shell) connections, and manipulation of trusted host information, posing a significant risk to the confidentiality, integrity, and availability of SSH communications via an insecure default configuration on Windows systems where the library automatically loads configuration files from the C:\etc directory, which can be created and modified by unprivileged local users.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://www.libssh.org/2026/02/10/libssh-0-12-0-and-0-11-4-security-releases/
- https://access.redhat.com/errata/RHSA-2026:7067
- https://access.redhat.com/security/cve/CVE-2025-14821
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14821.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14821
- https://bugzilla.redhat.com/show_bug.cgi?id=2423148
