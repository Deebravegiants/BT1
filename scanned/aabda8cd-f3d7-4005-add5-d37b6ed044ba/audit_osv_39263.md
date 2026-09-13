# [M] JumpServer: Remote Command Execution (RCE) via Jinja Template Injection in Applet Host Deployment

## Summary
Severity: Medium
Advisory: CVE-2026-44845
Aliases: GHSA-22h6-pcgh-9v7q
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-44845
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system. Prior to 4.10.17, an authenticated administrator with Applet Host management and deployment permissions can inject Jinja2 expressions into the IP/Host field or Core Service Address field, causing Ansible to evaluate ansible_host inventory data or playbook variables during Applet Host deployment and execute arbitrary commands on the JumpServer control node. This issue is fixed in version 4.10.17.

## References
- https://github.com/jumpserver/jumpserver/releases/tag/v4.10.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44845.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-22h6-pcgh-9v7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-44845
- https://github.com/jumpserver/jumpserver/commit/cc57ba0de5f6015746fae11cfc62402b11618e59
- https://github.com/jumpserver/jumpserver/pull/16749
- https://github.com/jumpserver/jumpserver/pull/16886
