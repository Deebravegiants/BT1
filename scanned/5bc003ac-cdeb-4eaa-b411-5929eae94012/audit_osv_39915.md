# [M] Open ISES Tickets < 3.44.2 Disabled TLS Certificate Verification in ajax/reports.php

## Summary
Severity: Medium
Advisory: CVE-2026-48246
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-48246
Type: osv

## Details
Open ISES Tickets before 3.44.2 disables TLS certificate verification in ajax/reports.php by setting CURLOPT_SSL_VERIFYPEER to false (and not setting CURLOPT_SSL_VERIFYHOST) when issuing outbound HTTPS requests for Google Maps Directions API lookups during incident report generation. An attacker positioned on the network path between the server and the remote endpoint can present a forged certificate to intercept, monitor, or modify the request and response, including any API keys or session-bearing data in transit.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48246.json
- https://github.com/openises/tickets/releases/tag/v3.44.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48246
- https://www.vulncheck.com/advisories/open-ises-tickets-disabled-tls-certificate-verification-in-ajax-reports-php
- https://github.com/openises/tickets/commit/ecfeb406a016766cae81c749e14b5145a9f2dbff
