# [M] CVE-2023-34204

## Summary
Severity: Medium
Advisory: CVE-2023-34204
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-34204
Type: osv

## Details
imapsync through 2.229 uses predictable paths under /tmp and /var/tmp in its default mode of operation. Both of these are typically world-writable, and thus (for example) an attacker can modify imapsync's cache and overwrite files belonging to the user who runs it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34204.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34204
- https://github.com/imapsync/imapsync/issues/399
