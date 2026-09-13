# [H] Apache CloudStack: OS Command Injection due to unsanitized mount command

## Summary
Severity: High
Advisory: CVE-2026-47359
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-47359
Type: osv

## Details
Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability in Apache CloudStack's NAS backup provider plugin. The addBackupRepository API (available since 4.20.0.0) and updateBackupRepository API (introduced in 4.22.0.0) accept unsanitized command options for the backup repository. A malicious operator account can exploit this to inject arbitrary commands that execute on the KVM hypervisor host when any account subsequently performs a backup restore.

This issue affects Apache CloudStack: from 4.20.0.0 through 4.20.3.0 and from 4.21.0.0 through 4.22.1.0.

Users are recommended to upgrade to version 4.20.3.1 or 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47359.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-47359
