# [M] CVE-2023-33717

## Summary
Severity: Medium
Advisory: CVE-2023-33717
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-33717
Type: osv

## Details
mp4v2 v2.1.3 was discovered to contain a memory leak when a method calling MP4File::ReadBytes() had allocated memory but did not catch exceptions thrown by ReadBytes()

## References
- https://github.com/enzo1982/mp4v2/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33717.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-33717
- https://github.com/enzo1982/mp4v2/issues/37
