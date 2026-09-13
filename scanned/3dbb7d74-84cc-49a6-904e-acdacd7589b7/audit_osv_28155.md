# [H] CVE-2024-28424

## Summary
Severity: High
Advisory: CVE-2024-28424
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-03-14
Source: https://osv.dev/vulnerability/CVE-2024-28424
Type: osv

## Details
zenml v0.55.4 was discovered to contain an arbitrary file upload vulnerability in the load function at /materializers/cloudpickle_materializer.py. This vulnerability allows attackers to execute arbitrary code via uploading a crafted file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28424.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-28424
- https://github.com/bayuncao/vul-cve-18
