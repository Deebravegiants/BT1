# [M] CVE-2023-50786

## Summary
Severity: Medium
Advisory: CVE-2023-50786
CVSS: 4.1 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2025-07-05
Source: https://osv.dev/vulnerability/CVE-2023-50786
Type: osv

## Details
Dradis through 4.16.0 allows referencing external images (resources) over HTTPS, instead of forcing the use of embedded (uploaded) images. This can be leveraged by an authorized author to attempt to steal the Net-NTLM hashes of other authors on a Windows domain network.

## References
- https://dradis.com/
- https://dradis.com/ce
- https://securiteam.io/2025/07/04/cve-2023-50786-dradis-ntlm-theft-vulnerability/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50786.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-50786
