# [M] Asterisk' res_pjsip_endpoint_identifier_ip: wrongly matches ALL unauthorized SIP requests

## Summary
Severity: Medium
Advisory: CVE-2024-35190
Aliases: GHSA-qqxj-v78h-hrf9
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35190
Type: osv

## Details
Asterisk is an open source private branch exchange and telephony toolkit. After upgrade to 18.23.0, ALL unauthorized SIP requests are identified as PJSIP Endpoint of local asterisk server. This vulnerability is fixed in 18.23.1, 20.8.1, and 21.3.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35190.json
- https://github.com/asterisk/asterisk/security/advisories/GHSA-qqxj-v78h-hrf9
- https://nvd.nist.gov/vuln/detail/CVE-2024-35190
- https://github.com/asterisk/asterisk/commit/85241bd22936cc15760fd1f65d16c98be7aeaf6d
- https://github.com/asterisk/asterisk/pull/600
- https://github.com/asterisk/asterisk/pull/602
