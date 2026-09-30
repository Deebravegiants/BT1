# [H] CVE-2019-14666

## Summary
Severity: High
Advisory: CVE-2019-14666
Aliases: GHSA-47hq-pfrr-jh5q
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-25
Source: https://osv.dev/vulnerability/CVE-2019-14666
Type: osv

## Details
GLPI through 9.4.3 is prone to account takeover by abusing the ajax/autocompletion.php autocompletion feature. The lack of correct validation leads to recovery of the token generated via the password reset functionality, and thus an authenticated attacker can set an arbitrary password for any user. This vulnerability can be exploited to take control of admin account. This vulnerability could be also abused to obtain other sensitive fields like API keys or password hashes.

## References
- https://github.com/glpi-project/glpi/security/advisories/GHSA-47hq-pfrr-jh5q
- https://www.tarlogic.com/advisories/Tarlogic-2019-GPLI-Account-Takeover.txt
