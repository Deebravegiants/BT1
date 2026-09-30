# [H] LPE on Multipass for macOS

## Summary
Severity: High
Advisory: CVE-2025-5199
Aliases: GHSA-2j82-p5cq-62p3
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-07-11
Source: https://osv.dev/vulnerability/CVE-2025-5199
Type: osv

## Details
In Canonical Multipass up to and including version 1.15.1 on macOS, incorrect default permissions allow a local attacker to escalate privileges by modifying files executed with administrative privileges by a Launch Daemon during system startup.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5199.json
- https://github.com/canonical/multipass/security/advisories/GHSA-2j82-p5cq-62p3
- https://nvd.nist.gov/vuln/detail/CVE-2025-5199
- https://github.com/canonical/multipass/pull/4115
- https://github.com/canonical/multipass
