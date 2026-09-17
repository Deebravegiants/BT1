# [H] Apache CloudStack: When downloading templates or ISOs, the management server and SSVM follow HTTP redirects with potentially dangerous consequences

## Summary
Severity: High
Advisory: CVE-2024-29007
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-29007
Type: osv

## Details
The CloudStack management server and secondary storage VM could be tricked into making requests to restricted or random resources by means of following 301 HTTP redirects presented by external servers when downloading templates or ISOs. Users are recommended to upgrade to version 4.18.1.1 or 4.19.0.1, which fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29007.json
- https://lists.apache.org/thread/82f46pv7mvh95ybto5hn8wlo6g8jhjvp
- https://nvd.nist.gov/vuln/detail/CVE-2024-29007
