# [M] Pimcore Privilege Defined With Unsafe Actions vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m4mv-rmr7-h5f5
CVE: CVE-2023-2983
CWE: CWE-267
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-m4mv-rmr7-h5f5
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.23

## Details
### Impact
A new user can privilege escalation to admin role which least config

### Patches
Update to version 10.5.23 or apply this patches manually
https://github.com/pimcore/pimcore/commit/c8f37b19c99cd82e4e558857d3e4d5476ea7228a.patch

### Workarounds
Apply patches manually: https://github.com/pimcore/pimcore/commit/c8f37b19c99cd82e4e558857d3e4d5476ea7228a.patch

### References
https://huntr.dev/bounties/6b2f33d3-2fd0-4d2d-ad7b-2c1e2417eeb1/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-m4mv-rmr7-h5f5
- https://nvd.nist.gov/vuln/detail/CVE-2023-2983
- https://github.com/pimcore/pimcore/commit/c8f37b19c99cd82e4e558857d3e4d5476ea7228a
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/6b2f33d3-2fd0-4d2d-ad7b-2c1e2417eeb1
