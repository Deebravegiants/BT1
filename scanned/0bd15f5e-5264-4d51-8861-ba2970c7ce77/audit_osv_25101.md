# [H] Plane 0.7.1 - Insecure file upload

## Summary
Severity: High
Advisory: CVE-2023-30791
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-07-15
Source: https://osv.dev/vulnerability/CVE-2023-30791
Type: osv

## Details
Plane version 0.7.1-dev allows an attacker to change the avatar of his profile, which allows uploading files with HTML extension that interprets both HTML and JavaScript.

## References
- https://fluidattacks.com/advisories/indio/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30791.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-30791
- https://github.com/makeplane/plane
