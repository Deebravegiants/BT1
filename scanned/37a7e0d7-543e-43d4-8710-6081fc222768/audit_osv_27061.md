# [C] RCE in Laragon

## Summary
Severity: Critical
Advisory: CVE-2024-0864
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2024-0864
Type: osv

## Details
Enabling Simple Ajax Uploader plugin included in Laragon open-source software allows for a remote code execution (RCE) attack via an improper input validation in a file_upload.php file which serves as an example.
By default, Laragon is not vulnerable until a user decides to use the aforementioned plugin.

## References
- https://laragon.org/
- https://cert.pl/en/posts/2024/02/CVE-2024-0864
- https://cert.pl/posts/2024/02/CVE-2024-0864
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0864.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0864
- https://github.com/leokhoa/laragon
