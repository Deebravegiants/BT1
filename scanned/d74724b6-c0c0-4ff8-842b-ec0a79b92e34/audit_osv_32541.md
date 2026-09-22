# [M] CVE-2025-32358

## Summary
Severity: Medium
Advisory: CVE-2025-32358
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2025-04-05
Source: https://osv.dev/vulnerability/CVE-2025-32358
Type: osv

## Details
In Zammad 6.4.x before 6.4.2, SSRF can occur. Authenticated admin users can enable webhooks in Zammad, which are triggered as POST requests when certain conditions are met. If a webhook endpoint returned a redirect response, Zammad would follow it automatically with another GET request. This could be abused by an attacker to cause GET requests for example in the local network.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32358.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32358
- https://zammad.com/en/advisories/zaa-2025-01
