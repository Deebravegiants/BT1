# [M] CVE-2024-52613

## Summary
Severity: Medium
Advisory: CVE-2024-52613
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-52613
Type: osv

## Details
A heap-based buffer under-read in tsMuxer version nightly-2024-05-12-02-01-18 allows attackers to cause Denial of Service (DoS) via a crafted MOV video file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52613.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52613
- https://github.com/justdan96/tsMuxer/issues/881
