# [M] Pimcore customers' list user password hash is disclosed

## Summary
Severity: Medium
Advisory: GHSA-j65r-g7q2-f8v3
CVE: CVE-2023-2881
CWE: CWE-257, CWE-522
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2023-05-25
Source: https://github.com/advisories/GHSA-j65r-g7q2-f8v3
Type: github-advisory

## Affected
- Packagist: `pimcore/customer-management-framework-bundle` — affected >=0 <3.3.10

## Details
### Impact
The customer view exposes the hashed password along with other deails. An attacker is then able to enum password of a particular id, likewise we can replace id with other user , for example 1015, password hash can be disclosed which can be further cracked with hashcat

### Patches
Update to version 3.3.10 or apply this patch manually https://github.com/pimcore/customer-data-framework/commit/d1d58c10313f080737dc1e71fab3beb12488a1e6.patch

### Workarounds
Apply https://github.com/pimcore/customer-data-framework/commit/d1d58c10313f080737dc1e71fab3beb12488a1e6.patch manually.

### References
https://huntr.dev/bounties/db6c32f4-742e-4262-8fd5-cefd0f133416/

## References
- https://github.com/pimcore/customer-data-framework/security/advisories/GHSA-j65r-g7q2-f8v3
- https://nvd.nist.gov/vuln/detail/CVE-2023-2881
- https://github.com/pimcore/customer-data-framework/commit/d1d58c10313f080737dc1e71fab3beb12488a1e6
- https://github.com/pimcore/customer-data-framework
- https://huntr.dev/bounties/db6c32f4-742e-4262-8fd5-cefd0f133416
