# [C] Git Argument Injection in prefecthq/prefect

## Summary
Severity: Critical
Advisory: CVE-2026-5366
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-20
Source: https://osv.dev/vulnerability/CVE-2026-5366
Type: osv

## Details
Prefect version 3.6.23 is vulnerable to remote code execution due to improper handling of user-controlled input in the `GitRepository` storage class. The `commit_sha` parameter, which is passed to git commands, lacks validation and does not include a `--` separator to distinguish user input from git flags. This allows attackers to inject arbitrary git flags, such as `--upload-pack`, enabling execution of external programs. Additionally, the `directories` parameter can be exploited to inject git flags during sparse-checkout operations. These vulnerabilities allow any user with deployment creation permissions to execute arbitrary commands on worker machines, compromising shared work pools in multi-tenant environments.

## References
- https://huntr.com/bounties/e2e88a0f-a8f6-49c9-94c5-e98dc385f07a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5366.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5366
