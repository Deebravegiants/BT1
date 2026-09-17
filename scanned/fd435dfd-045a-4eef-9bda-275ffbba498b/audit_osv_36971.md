# [H] Rollup 4 has Arbitrary File Write via Path Traversal

## Summary
Severity: High
Advisory: CVE-2026-27606
Aliases: GHSA-mw96-cpmx-2vgc
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27606
Type: osv

## Details
Rollup is a module bundler for JavaScript. Versions prior to 2.80.0, 3.30.0, and 4.59.0 of the Rollup module bundler (specifically v4.x and present in current source) is vulnerable to an Arbitrary File Write via Path Traversal. Insecure file name sanitization in the core engine allows an attacker to control output filenames (e.g., via CLI named inputs, manual chunk aliases, or malicious plugins) and use traversal sequences (`../`) to overwrite files anywhere on the host filesystem that the build process has permissions for. This can lead to persistent Remote Code Execution (RCE) by overwriting critical system or user configuration files. Versions 2.80.0, 3.30.0, and 4.59.0 contain a patch for the issue.

## References
- https://github.com/rollup/rollup/releases/tag/v2.80.0
- https://github.com/rollup/rollup/releases/tag/v3.30.0
- https://github.com/rollup/rollup/releases/tag/v4.59.0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27606.json
- https://access.redhat.com/errata/RHSA-2026:10175
- https://access.redhat.com/errata/RHSA-2026:13508
- https://access.redhat.com/errata/RHSA-2026:13512
- https://access.redhat.com/errata/RHSA-2026:13545
- https://access.redhat.com/errata/RHSA-2026:5132
- https://access.redhat.com/errata/RHSA-2026:5649
- https://access.redhat.com/errata/RHSA-2026:5665
- https://access.redhat.com/errata/RHSA-2026:6174
- https://access.redhat.com/errata/RHSA-2026:6802
- https://access.redhat.com/errata/RHSA-2026:8483
- https://access.redhat.com/security/cve/CVE-2026-27606
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27606.json
- https://github.com/rollup/rollup/security/advisories/GHSA-mw96-cpmx-2vgc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27606
- https://bugzilla.redhat.com/show_bug.cgi?id=2442530
- https://github.com/rollup/rollup/commit/c60770d7aaf750e512c1b2774989ea4596e660b2
