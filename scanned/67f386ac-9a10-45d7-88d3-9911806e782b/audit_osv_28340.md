# [M] CVE-2024-31670

## Summary
Severity: Medium
Advisory: CVE-2024-31670
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-12-12
Source: https://osv.dev/vulnerability/CVE-2024-31670
Type: osv

## Details
rizin before v0.6.3 is vulnerable to Buffer Overflow via create_cache_bins, read_cache_accel, and rz_dyldcache_new_buf functions in librz/bin/format/mach0/dyldcache.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31670.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31670
- https://github.com/rizinorg/rizin/commit/75bac3088b2ec173e22d4be9d525ceacc987cf02
