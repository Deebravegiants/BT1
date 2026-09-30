# [H] CVE-2018-25081

## Summary
Severity: High
Advisory: CVE-2018-25081
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-09
Source: https://osv.dev/vulnerability/CVE-2018-25081
Type: osv

## Details
Bitwarden through 2023.2.1 offers password auto-fill within a cross-domain IFRAME element. NOTE: the vendor's position is that there have been important legitimate cross-domain configurations (e.g., an apple.com IFRAME element on the icloud.com website) and that "Auto-fill on page load" is not enabled by default.

## References
- https://cdn.bitwarden.net/misc/Bitwarden%20Security%20Assessment%20Report.pdf
- https://github.com/bitwarden/clients/releases
- https://news.ycombinator.com/item?id=35075861
- https://flashpoint.io/blog/bitwarden-password-pilfering/
