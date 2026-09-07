# [H] TYPO3 CMS Possible Insecure Deserialization in Extbase Request Handling

## Summary
Severity: High
Advisory: GHSA-hh95-5xm5-v8v7
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-hh95-5xm5-v8v7
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.30
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.12

## Details
It has been discovered that request handling in Extbase can be vulnerable to insecure deserialization. User submitted payload has to be signed with a corresponding HMAC-SHA1 using the sensitive TYPO3 encryptionKey as secret - invalid or unsigned payload is not deserialized.

However, since sensitive information could have been leaked by accident (e.g. in repositories or in commonly known and unprotected backup files), there is the possibility that attackers know the private encryptionKey and are able to calculate the required HMAC-SHA1 to allow a malicious payload to be deserialized.

Requirements for successfully exploiting this vulnerability (all of the following):

- rendering at least one Extbase plugin in the frontend
- encryptionKey has been leaked (from LocalConfiguration.php or corresponding .env file)

## References
- https://github.com/TYPO3/typo3/commit/57e4ed35a6e58521a931855e702b2688b3bc3d62
- https://github.com/TYPO3/typo3/commit/b1626ad8fd4aebedc15e424a76f86094d78b2564
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-12-17-7.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-psa-2019-011
