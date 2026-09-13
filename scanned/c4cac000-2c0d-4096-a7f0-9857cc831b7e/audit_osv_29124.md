# [C] FOG has a command injection in /fog/management/export.php?filename=

## Summary
Severity: Critical
Advisory: CVE-2024-39914
Aliases: GHSA-7h44-6vq6-cq8j
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-39914
Type: osv

## Details
FOG is a cloning/imaging/rescue suite/inventory management system. Prior to 1.5.10.34, packages/web/lib/fog/reportmaker.class.php in FOG was affected by a command injection via the filename parameter to /fog/management/export.php. This vulnerability is fixed in 1.5.10.34.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39914.json
- https://github.com/FOGProject/fogproject/security/advisories/GHSA-7h44-6vq6-cq8j
- https://nvd.nist.gov/vuln/detail/CVE-2024-39914
- https://github.com/FOGProject/fogproject/commit/2413bc034753c32799785e9bf08164ccd0a2759f
