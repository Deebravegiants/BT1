# [M] Mautic vulnerable to secret data exfiltration via symfony parameters

## Summary
Severity: Medium
Advisory: GHSA-4hjq-422q-4vpx
CVE: CVE-2021-27908
CWE: CWE-732, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2021-04-06
Source: https://github.com/advisories/GHSA-4hjq-422q-4vpx
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <3.3.2

## Details
### Impact
Symfony parameters (which is what Mautic transforms configuration parameters into) can be used within other Symfony parameters by design. However, this also means that an admin who is normally not privy to certain parameters, such as database credentials, could expose them by leveraging any of the free text fields in Mautic’s configuration that are used in publicly facing parts of the application.

For example,

1. Go to Configuration page -> Landing Page Settings -> Analytics script and enter this: <`script> console.log("db password is: %mautic.db_password%"); </script>`
2. Visit any landing page and open the JS dev console. You will see the following message with real instance db password: `db password is: <real password>`

Risk rating: ModerateCVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:L

### Patches
Upgrade to 3.3.2

### Workarounds
No

### References
No

### For more information
If you have any questions or comments about this advisory:

* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-4hjq-422q-4vpx
- https://nvd.nist.gov/vuln/detail/CVE-2021-27908
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mautic/core/CVE-2021-27908.yaml
- https://github.com/mautic/mautic
