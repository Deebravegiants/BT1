# [M] Server-Side Request Forgery vulnerability in various APIs in Misskey

## Summary
Severity: Medium
Advisory: CVE-2024-52579
Aliases: GHSA-5q3h-wpfw-hjjw
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-52579
Type: osv

## Details
Misskey is an open source, federated social media platform. Some APIs using `HttpRequestService` do not properly check the target host. This vulnerability allows an attacker to send POST or GET requests to the internal server, which may result in a SSRF attack.It allows an attacker to send POST or GET requests (with some controllable URL parameters) to private IPs, enabling further attacks on internal servers. This issue has been addressed in version 2024.11.0-alpha.3. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52579.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-5q3h-wpfw-hjjw
- https://nvd.nist.gov/vuln/detail/CVE-2024-52579
