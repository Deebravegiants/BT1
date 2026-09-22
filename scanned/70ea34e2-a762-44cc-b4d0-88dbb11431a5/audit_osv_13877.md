# [H] CVE-2018-3761

## Summary
Severity: High
Advisory: CVE-2018-3761
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-3761
Type: osv

## Details
Nextcloud Server before 12.0.8 and 13.0.3 suffer from improper authentication on the OAuth2 token endpoint. Missing checks potentially allowed handing out new tokens in case the OAuth2 client was partly compromised.

## References
- https://hackerone.com/reports/343111
- https://nextcloud.com/security/advisory/?id=nc-sa-2018-003
