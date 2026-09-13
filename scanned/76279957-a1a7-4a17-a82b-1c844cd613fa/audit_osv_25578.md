# [H] Insights-client: unsafe handling of temporary files and directories

## Summary
Severity: High
Advisory: CVE-2023-3972
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-01
Source: https://osv.dev/vulnerability/CVE-2023-3972
Type: osv

## Details
A vulnerability was found in insights-client. This security issue occurs because of insecure file operations or unsafe handling of temporary files and directories that lead to local privilege escalation. Before the insights-client has been registered on the system by root, an unprivileged local user or attacker could create the /var/tmp/insights-client directory (owning the directory with read, write, and execute permissions) on the system. After the insights-client is registered by root, an attacker could then control the directory content that insights are using by putting malicious scripts into it and executing arbitrary code as root (trivially bypassing SELinux protections because insights processes are allowed to disable SELinux system-wide).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2023:6264
- https://access.redhat.com/errata/RHSA-2023:6282
- https://access.redhat.com/errata/RHSA-2023:6283
- https://access.redhat.com/errata/RHSA-2023:6284
- https://access.redhat.com/errata/RHSA-2023:6795
- https://access.redhat.com/errata/RHSA-2023:6796
- https://access.redhat.com/errata/RHSA-2023:6798
- https://access.redhat.com/errata/RHSA-2023:6811
- https://access.redhat.com/security/cve/CVE-2023-3972
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3972.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3972
- https://bugzilla.redhat.com/show_bug.cgi?id=2227027
- https://github.com/RedHatInsights/insights-core/pull/3878
