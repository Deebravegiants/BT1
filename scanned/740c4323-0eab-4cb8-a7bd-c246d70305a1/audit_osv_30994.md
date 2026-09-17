# [C] CVE-2024-57520

## Summary
Severity: Critical
Advisory: CVE-2024-57520
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-05
Source: https://osv.dev/vulnerability/CVE-2024-57520
Type: osv

## Details
Insecure Permissions vulnerability in asterisk v22 allows a remote attacker to execute arbitrary code via the action_createconfig function. NOTE: this is disputed by the Supplier because the impact is limited to creating empty files outside of the Asterisk product directory (aka directory traversal) and the attack can only be performed by a privileged user who has the ability to manage the configuration.

## References
- https://gist.github.com/hyp164D1/ae76ab25acfbe263b2ed7b24b6e5c621
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57520.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57520
- https://github.com/asterisk/asterisk/issues/1122
