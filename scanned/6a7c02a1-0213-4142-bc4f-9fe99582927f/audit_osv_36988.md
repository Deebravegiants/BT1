# [H] iccDEV has HBO in CIccTagTextDescription::Release()

## Summary
Severity: High
Advisory: CVE-2026-27692
Aliases: GHSA-3869-prw8-gjqr
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27692
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. In versions up to and including 2.3.1.4, heap-buffer-overflow read occurs during CIccTagTextDescription::Release() when strlen() reads past a heap buffer while parsing ICC profile XML text description tags, causing a crash. Commit 29d088840b962a7cdd35993dfabc2cb35a049847 fixes the issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27692.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-3869-prw8-gjqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27692
- https://github.com/InternationalColorConsortium/iccDEV/issues/609
- https://github.com/InternationalColorConsortium/iccDEV/commit/29d088840b962a7cdd35993dfabc2cb35a049847
- https://github.com/InternationalColorConsortium/iccDEV/pull/610
