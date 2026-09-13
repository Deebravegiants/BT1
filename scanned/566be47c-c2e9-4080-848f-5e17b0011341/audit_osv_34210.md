# [H] CVE-2025-55763

## Summary
Severity: High
Advisory: CVE-2025-55763
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-29
Source: https://osv.dev/vulnerability/CVE-2025-55763
Type: osv

## Details
Buffer Overflow in the URI parser of CivetWeb 1.14 through 1.16 (latest) allows a remote attacker to achieve remote code execution via a crafted HTTP request. This vulnerability is triggered during request processing and may allow an attacker to corrupt heap memory, potentially leading to denial of service or arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55763.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55763
- https://github.com/civetweb/civetweb
- https://github.com/krispybyte/CVE-2025-55763
