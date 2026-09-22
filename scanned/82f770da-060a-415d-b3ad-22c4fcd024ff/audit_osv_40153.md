# [H] Apache CloudStack: Improper access control in Userdata reference APIs

## Summary
Severity: High
Advisory: CVE-2026-50222
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-50222
Type: osv

## Details
Missing Authorization, Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache CloudStack's Userdata reference APIs.

Several userdata-related APIs in Apache CloudStack, including deleteUserData, linkUserDataToTemplate, resetUserDataForVirtualMachine, deployVirtualMachine, and updateVirtualMachine, exhibit missing or insufficient access control validation, potentially allowing cross-tenant/cross-account access to userdata resources that belong to other tenants.

This issue affects Apache CloudStack: from 4.18.0.0 through 4.20.3.0 and from 4.21.0.0 through 4.22.1.0.

The deleteCniConfiguration API, introduced in 4.21.0.0, also exhibits similar behaviour and lacks access validation.

Users are recommended to upgrade to version 4.20.3.1 or 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50222.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-50222
