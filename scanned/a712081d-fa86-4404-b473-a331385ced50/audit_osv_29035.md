# [H] CVE-2024-39134

## Summary
Severity: High
Advisory: CVE-2024-39134
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2024-39134
Type: osv

## Details
A Stack Buffer Overflow vulnerability in zziplibv 0.13.77 allows attackers to cause a denial of service via the __zzip_fetch_disk_trailer() function at /zzip/zip.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39134.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39134
- https://github.com/gdraheim/zziplib/issues/165
