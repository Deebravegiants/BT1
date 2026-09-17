# [C] Cross-project instance move bypasses all project restrictions allowing host command execution

## Summary
Severity: Critical
Advisory: CVE-2026-63300
Aliases: GHSA-5g5r-wh97-qcq2
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-63300
Type: osv

## Details
An improper validation vulnerability in the instancePostMigration function in lxd/instance_post.go of LXD allows an authenticated attacker with can_create_instances permissions on a restricted project to bypass project-level security restrictions. When migrating an instance between projects, LXD fails to validate the instance's configuration against the target project's enforced restrictions (such as restricted.containers.lowlevel, restricted.devices.*, and restricted.networks.access). An attacker can exploit this by creating a disallowed or high-privilege instance in an unrestricted project and subsequently moving it into the restricted project.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63300.json
- https://github.com/canonical/lxd/security/advisories/GHSA-5g5r-wh97-qcq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-63300
- https://github.com/canonical/lxd/pull/18605
- https://github.com/canonical/lxd/pull/18651
- https://github.com/canonical/lxd
