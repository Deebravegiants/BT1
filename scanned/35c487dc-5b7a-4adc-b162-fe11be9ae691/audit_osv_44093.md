# [M] CVE-2026-79653

## Summary
Severity: Medium
Advisory: CVE-2026-79653
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-79653
Type: osv

## Details
In Eclipse SW360 versions 19.0.0, 19.1.0, 19.2.0, 20.0.0, 20.1.0, if the system is configured to use file system storage with config key enable.attachment.store.to.file.system, the attacker can manipulate the filename upon upload and can essentially cause arbitrary file path traversal.




The immediate workaround is to disable enable.attachment.store.to.file.system or update to fixed versions.

## References
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/765
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79653.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-79653
- https://github.com/eclipse-sw360/sw360/pull/4516
- https://github.com/eclipse-sw360/sw360/pull/4517
- https://github.com/eclipse-sw360/sw360/pull/4518
