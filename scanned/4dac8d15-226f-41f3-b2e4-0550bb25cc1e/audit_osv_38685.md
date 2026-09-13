# [H] Zen Browser MAR updater ships with signature verification removed — unsigned updates accepted

## Summary
Severity: High
Advisory: CVE-2026-41431
Aliases: GHSA-qpj9-m8jc-mw6q
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-41431
Type: osv

## Details
Zen is a firefox-based browser. Prior to 1.19.9b, Zen Browser ships a Mozilla Application Resource (MAR) updater (org.mozilla.updater) that has had all MAR signature verification stripped from the Firefox codebase it was forked from. The MAR files served to users contain zero cryptographic signatures, and the updater binary contains zero cryptographic verification code. This eliminates the defense-in-depth that MAR signing provides. If the update server or GitHub release pipeline is compromised, arbitrary unsigned code can be delivered to all Zen users via the auto-update mechanism. This vulnerability is fixed in 1.19.9b.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41431.json
- https://github.com/zen-browser/desktop/security/advisories/GHSA-qpj9-m8jc-mw6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-41431
- https://github.com/zen-browser/desktop/commit/270db6d6713d2c6c14d9df0b4bc7662843d3d54e
