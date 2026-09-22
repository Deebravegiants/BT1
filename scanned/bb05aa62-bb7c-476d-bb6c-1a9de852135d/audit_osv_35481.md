# [M] TOCTOU race in Linenoise enables arbitrary file overwrite and permission changes

## Summary
Severity: Medium
Advisory: CVE-2025-9810
CVSS: 6.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2025-09-01
Source: https://osv.dev/vulnerability/CVE-2025-9810
Type: osv

## Details
TOCTOU  in linenoiseHistorySave in linenoise allows local attackers to overwrite arbitrary files and change permissions via a symlink race between fopen("w") on the history path and subsequent chmod() on the same path.

## References
- https://github.com/antirez/linenoise/blob/4111f1d6cd29e136b4e86a25d1dd859a1e00813b/linenoise.c#L1321
- https://github.com/antirez/linenoise/blob/master/linenoise.c#L1321
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9810.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-9810
- https://github.com/antirez/linenoise/commit/f2558e1e588b1ba384ec73a2cf5c9a46409753db
- https://github.com/antirez/linenoise/pull/202
