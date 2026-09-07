# [M] stormpath/sdk uses Insecure Random Number Generator

## Summary
Severity: Medium
Advisory: GHSA-q8fc-v85f-78pw
CWE: CWE-338
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-29
Source: https://github.com/advisories/GHSA-q8fc-v85f-78pw
Type: github-advisory

## Affected
- Packagist: `stormpath/sdk` — affected >=0

## Details
The vulnerability pertains to the usage of an insecure random number generator (RNG) in the "stormpath-sdk-php" library. Specifically, the issue is present in the generation of UUID (Universally Unique Identifier) version 4 within the codebase.

## References
- https://github.com/stormpath/stormpath-sdk-php/issues/132
- https://github.com/FriendsOfPHP/security-advisories/blob/master/stormpath/sdk/2017-11-20.yaml
- https://github.com/stormpath/stormpath-sdk-php
- https://github.com/stormpath/stormpath-sdk-php/blob/15aee3007b8aa41c20cdf28fd650b8a2368a7fa9/src/Util/UUID.php#L167-L181
- https://github.com/stormpath/stormpath-sdk-php/blob/62698ea98ef89217f932e28cf3e511d39af3b4cf/src/Authc/Api/ApiKeyEncryptionOptions.php#L48-L50
