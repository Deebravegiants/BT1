# [M] Blind SSRF via server URL input in the Nextcloud Mail app

## Summary
Severity: Medium
Advisory: CVE-2023-23943
Aliases: GHSA-8gcx-r739-9pf6
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2023-02-06
Source: https://osv.dev/vulnerability/CVE-2023-23943
Type: osv

## Details
Nextcloud mail is an email app for the nextcloud home server platform. In affected versions the SMTP, IMAP and Sieve host fields allowed to scan for internal services and servers reachable from within the local network of the Nextcloud Server. It is recommended that the Nextcloud Maill app is upgraded to 1.15.0 or 2.2.2. The only known workaround for this issue is to completely disable the nextcloud mail app.

## References
- https://hackerone.com/reports/1736390
- https://hackerone.com/reports/1741525
- https://hackerone.com/reports/1746582
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23943.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-8gcx-r739-9pf6
- https://nvd.nist.gov/vuln/detail/CVE-2023-23943
- https://github.com/nextcloud/mail/pull/7796
