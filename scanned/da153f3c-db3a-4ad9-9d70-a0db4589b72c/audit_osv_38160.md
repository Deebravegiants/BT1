# [H] Vim modeline bypass via various options affects Vim < 9.2.0276

## Summary
Severity: High
Advisory: CVE-2026-34982
Aliases: GHSA-8h6p-m6gr-mpw9
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-34982
Type: osv

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0276, a modeline sandbox bypass in Vim allows arbitrary OS command execution when a user opens a crafted file. The `complete`, `guitabtooltip` and `printheader` options are missing the `P_MLE` flag, allowing a modeline to be executed. Additionally, the `mapset()` function lacks a `check_secure()` call, allowing it to be abused from sandboxed expressions. Commit 9.2.0276 fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/04/01/1
- https://github.com/vim/vim/releases/tag/v9.2.0276
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34982.json
- https://access.redhat.com/errata/RHSA-2026:11389
- https://access.redhat.com/errata/RHSA-2026:11509
- https://access.redhat.com/errata/RHSA-2026:11510
- https://access.redhat.com/errata/RHSA-2026:19073
- https://access.redhat.com/errata/RHSA-2026:19224
- https://access.redhat.com/errata/RHSA-2026:21275
- https://access.redhat.com/errata/RHSA-2026:22634
- https://access.redhat.com/errata/RHSA-2026:28049
- https://access.redhat.com/errata/RHSA-2026:28050
- https://access.redhat.com/errata/RHSA-2026:28133
- https://access.redhat.com/errata/RHSA-2026:30078
- https://access.redhat.com/errata/RHSA-2026:30087
- https://access.redhat.com/errata/RHSA-2026:30088
- https://access.redhat.com/errata/RHSA-2026:30089
- https://access.redhat.com/errata/RHSA-2026:30900
- https://access.redhat.com/errata/RHSA-2026:33453
- https://access.redhat.com/errata/RHSA-2026:34476
