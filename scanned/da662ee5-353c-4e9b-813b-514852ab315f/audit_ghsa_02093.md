# [C] Time-of-check Time-of-use (TOCTOU) Race Condition in league/flysystem

## Summary
Severity: Critical
Advisory: GHSA-9f46-5r25-5wfm
CVE: CVE-2021-32708
CWE: CWE-367
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-9f46-5r25-5wfm
Type: github-advisory

## Affected
- Packagist: `league/flysystem` — affected >=0 <1.1.4
- Packagist: `league/flysystem` — affected >=2.0.0 <2.1.1

## Details
### Impact

The whitespace normalisation using in 1.x and 2.x removes any unicode whitespace. Under certain specific conditions this could potentially allow a malicious user to execute code remotely.

The conditions: 

- A user is allowed to supply the path or filename of an uploaded file.
- The supplied path or filename is not checked against unicode chars.
- The supplied pathname checked against an extension deny-list, not an allow-list.
- The supplied path or filename contains a unicode whitespace char in the extension.
- The uploaded file is stored in a directory that allows PHP code to be executed.

Given these conditions are met a user can upload and execute arbitrary code on the system under attack.

### Patches

The unicode whitespace removal has been replaced with a rejection (exception).

The library has been patched in:
- 1.x: https://github.com/thephpleague/flysystem/commit/f3ad69181b8afed2c9edf7be5a2918144ff4ea32
- 2.x: https://github.com/thephpleague/flysystem/commit/a3c694de9f7e844b76f9d1b61296ebf6e8d89d74

### Workarounds

For 1.x users, upgrade to 1.1.4. For 2.x users, upgrade to 2.1.1.

## References
- https://github.com/thephpleague/flysystem/security/advisories/GHSA-9f46-5r25-5wfm
- https://nvd.nist.gov/vuln/detail/CVE-2021-32708
- https://github.com/thephpleague/flysystem/commit/a3c694de9f7e844b76f9d1b61296ebf6e8d89d74
- https://github.com/thephpleague/flysystem/commit/f3ad69181b8afed2c9edf7be5a2918144ff4ea32
- https://github.com/FriendsOfPHP/security-advisories/blob/master/league/flysystem/CVE-2021-32708.yaml
- https://github.com/thephpleague/flysystem
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NWPTENBYKI2IG47GI4DHAACLNRLTWUR5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RNZSWK4GOMJOOHKLZEOE5AQSLC4DNCRZ
- https://packagist.org/packages/league/flysystem
