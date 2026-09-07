# [M] "powermail" (powermail) Insecure Direct Object Reference (IDOR)

## Summary
Severity: Medium
Advisory: GHSA-p652-xcgx-f85m
CVE: CVE-2024-45232
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L/E:F/RL:O/RC:C (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-p652-xcgx-f85m
Type: github-advisory

## Affected
- Packagist: `in2code/powermail` — affected >=11.0.0 <12.4.0
- Packagist: `in2code/powermail` — affected >=9.0.0 <10.9.0
- Packagist: `in2code/powermail` — affected >=8.0.0 <8.5.0
- Packagist: `in2code/powermail` — affected >=0 <7.5.0

## Details
An issue was discovered in powermail extension through 12.3.5 for TYPO3. It fails to validate the mail parameter of the confirmationAction, resulting in Insecure Direct Object Reference (IDOR). An unauthenticated attacker can use this to display the user-submitted data of all forms persisted by the extension. This can only be exploited when the extension is configured to save submitted form data to the database (`plugin.tx_powermail.settings.db.enable=1`), which however is the default setting of the extension. The fixed versions are 7.5.0, 8.5.0, 10.9.0, and 12.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45232
- https://github.com/in2code-de/powermail/commit/061756732357206f2f13bf39a0676dd266ec9586
- https://github.com/in2code-de/powermail/commit/ac402d4972c77dd119c8db6ffe594c15e8ae0bc5
- https://github.com/in2code-de/powermail/commit/e2ddfaa06d29019d60be02b5a3da04b237ed760b
- https://github.com/in2code-de/powermail/commit/f58d70311799ae5f6acbec52ea9206d21eba91bb
- https://github.com/FriendsOfPHP/security-advisories/blob/master/in2code/powermail/CVE-2024-45232.yaml
- https://github.com/in2code-de/powermail
- https://typo3.org/security/advisory/typo3-ext-sa-2024-006
