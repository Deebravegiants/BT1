# [M] Tauri's readDir Endpoint Scope can be Bypassed With Symbolic Links

## Summary
Severity: Medium
Advisory: GHSA-28m8-9j7v-x499
CVE: CVE-2022-39215
CWE: CWE-22, CWE-59
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-28m8-9j7v-x499
Type: github-advisory

## Affected
- crates.io: `tauri` — affected >=0 <1.0.6

## Details
### Impact
Due to missing canonicalization when `readDir` is called recursively, it was possible to display directory listings outside of the defined `fs` scope. This required a crafted symbolic link or junction folder inside an allowed path of the `fs` scope. No arbitrary file content could be leaked.


### Patches
The issue has been resolved in https://github.com/tauri-apps/tauri/pull/5123 and the implementation now properly checks if the
requested (sub) directory is a symbolic link outside of the defined `scope`.

### Workarounds
Disable the `readDir` endpoint in the `allowlist` inside the `tauri.conf.json`.

### For more information

This issue was initially reported by [martin-ocasek]( https://github.com/martin-ocasek) in [#4882](https://github.com/tauri-apps/tauri/issues/4882).

If you have any questions or comments about this advisory:
* Open an issue in [tauri](https://github.com/tauri-apps/tauri)
* Email us at [security@tauri.app](mailto:security@tauri.app)

## References
- https://github.com/tauri-apps/tauri/security/advisories/GHSA-28m8-9j7v-x499
- https://nvd.nist.gov/vuln/detail/CVE-2022-39215
- https://github.com/tauri-apps/tauri/issues/4882
- https://github.com/tauri-apps/tauri/pull/5123
- https://github.com/tauri-apps/tauri/pull/5123/commits/1f9b9e8d26a2c915390323e161020bcb36d44678
- https://github.com/tauri-apps/tauri/commit/bb178829086e80916f9be190f02d83bc25802799
- https://github.com/tauri-apps/tauri
- https://github.com/tauri-apps/tauri/releases/tag/tauri-v1.0.6
- https://rustsec.org/advisories/RUSTSEC-2022-0088.html
