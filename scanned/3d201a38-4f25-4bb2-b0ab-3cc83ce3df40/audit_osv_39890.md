# [C] Unsafe Client MIME Type Handling Can Enable Arbitrary File Upload in plank/laravel-mediable

## Summary
Severity: Critical
Advisory: CVE-2026-4809
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-4809
Type: osv

## Details
plank/laravel-mediable through version 6.4.0 can allow upload of a dangerous file type when an application using the package accepts or prefers a client-supplied MIME type during file upload handling. In that configuration, a remote attacker can submit a file containing executable PHP code while declaring a benign image MIME type, resulting in arbitrary file upload.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4809.json
- https://github.com/plank/laravel-mediable
- https://github.com/plank/laravel-mediable/releases/tag/6.4.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-4809
