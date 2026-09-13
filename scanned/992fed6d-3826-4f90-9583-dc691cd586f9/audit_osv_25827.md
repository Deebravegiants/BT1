# [M] Require strict cookies for image proxy requests in Nextcloud Mail

## Summary
Severity: Medium
Advisory: CVE-2023-45660
Aliases: GHSA-8j9x-fmww-qr37
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-10-16
Source: https://osv.dev/vulnerability/CVE-2023-45660
Type: osv

## Details
Nextcloud mail is an email app for the Nextcloud home server platform. In affected versions a missing check of origin, target and cookies allows for an attacker to abuse the proxy endpoint to denial of service a third server. It is recommended that the Nextcloud Mail is upgraded to 2.2.8 or 3.3.0. There are no known workarounds for this vulnerability.

## References
- https://hackerone.com/reports/1895874
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45660.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-8j9x-fmww-qr37
- https://nvd.nist.gov/vuln/detail/CVE-2023-45660
- https://github.com/nextcloud/mail/pull/8459
