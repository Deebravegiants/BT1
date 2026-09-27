# [H] CVE-2024-31744

## Summary
Severity: High
Advisory: CVE-2024-31744
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-19
Source: https://osv.dev/vulnerability/CVE-2024-31744
Type: osv

## Details
In Jasper 4.2.2, the jpc_streamlist_remove function in src/libjasper/jpc/jpc_dec.c:2407 has an assertion failure vulnerability, allowing attackers to cause a denial of service attack through a specific image file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31744.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31744
- https://github.com/jasper-software/jasper/issues/381
- https://github.com/jasper-software/jasper/commit/6d084c53a77762f41bb5310713a5f1872fef55f5
