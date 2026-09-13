# [C] Apache CloudStack: x-forwarded-for HTTP header parsed by default

## Summary
Severity: Critical
Advisory: CVE-2024-29006
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-29006
Type: osv

## Details
By default the CloudStack management server honours the x-forwarded-for HTTP header and logs it as the source IP of an API request. This could lead to authentication bypass and other operational problems should an attacker decide to spoof their IP address this way. Users are recommended to upgrade to CloudStack version 4.18.1.1 or 4.19.0.1, which fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29006.json
- https://lists.apache.org/thread/82f46pv7mvh95ybto5hn8wlo6g8jhjvp
- https://nvd.nist.gov/vuln/detail/CVE-2024-29006
