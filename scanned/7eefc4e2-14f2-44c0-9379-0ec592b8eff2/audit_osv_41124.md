# [H] Pinpoint - Insecure Session Cookie Attributes in pinpointJwt

## Summary
Severity: High
Advisory: CVE-2026-57948
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-57948
Type: osv

## Details
Pinpoint through version 3.1.0 contains an insecure session management vulnerability that allows attackers to access the pinpointJwt session cookie due to missing HttpOnly and Secure attributes, enabling JavaScript access via document.cookie and cleartext transmission over HTTP. Attackers can exploit stored or reflected cross-site scripting vulnerabilities to exfiltrate the session token or intercept it through network sniffing to perform session hijacking.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57948.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57948
- https://www.vulncheck.com/advisories/pinpoint-insecure-session-cookie-attributes-in-pinpointjwt
- https://github.com/pinpoint-apm/pinpoint/issues/13858
- https://github.com/pinpoint-apm/pinpoint
