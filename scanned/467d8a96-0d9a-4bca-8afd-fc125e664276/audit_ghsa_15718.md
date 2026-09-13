# [M] ZITADEL "ignoring unknown usernames" vulnerability

## Summary
Severity: Medium
Advisory: GHSA-567v-6hmg-6qg7
CVE: CVE-2024-41952
CWE: CWE-203
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-567v-6hmg-6qg7
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=2.53.0 <2.53.9
- Go: `github.com/zitadel/zitadel` — affected >=2.54.0 <2.54.8
- Go: `github.com/zitadel/zitadel` — affected >=2.55.0 <2.55.5
- Go: `github.com/zitadel/zitadel` — affected >=2.56.0 <2.56.2
- Go: `github.com/zitadel/zitadel` — affected >=2.57.0 <2.57.1
- Go: `github.com/zitadel/zitadel` — affected >=2.58.0 <2.58.1
- Go: `github.com/zitadel/zitadel` — affected >=0.0.0-20230609131415-dafa8ab4dfe8 <0.0.0-20240731122357-a1d24353db4d
- Go: `github.com/zitadel/zitadel` — affected >=1.80.0-v2.20.0.20230609131415-dafa8ab4dfe8 <1.80.0-v2.20.0.20240731122357-a1d24353db4d

## Details
### Impact

ZITADEL administrators can enable a setting called "Ignoring unknown usernames" which helps mitigate attacks that try to guess/enumerate usernames. If enabled, ZITADEL will show the password prompt even if the user doesn't exist and report "Username or Password invalid".
Due to a implementation change to prevent deadlocks calling the database, the flag would not be correctly respected in all cases and an attacker would gain information if an account exist within ZITADEL, since the error message shows "object not found" instead of the generic error message.

### Patches

2.x versions are fixed on >= [2.58.1](https://github.com/zitadel/zitadel/releases/tag/v2.58.1)
2.57.x versions are fixed on >= [2.57.1](https://github.com/zitadel/zitadel/releases/tag/v2.57.1)
2.56.x versions are fixed on >= [2.56.2](https://github.com/zitadel/zitadel/releases/tag/v2.56.2)
2.55.x versions are fixed on >= [2.55.5](https://github.com/zitadel/zitadel/releases/tag/v2.55.5)
2.54.x versions are fixed on >= [2.54.8](https://github.com/zitadel/zitadel/releases/tag/v2.54.8)
2.53.x versions are fixed on >= [2.53.9](https://github.com/zitadel/zitadel/releases/tag/v2.53.9)

ZITADEL recommends upgrading to the latest versions available in due course.

### Workarounds

There is no workaround since a patch is already available.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-567v-6hmg-6qg7
- https://nvd.nist.gov/vuln/detail/CVE-2024-41952
- https://github.com/zitadel/zitadel/commit/0ab0c645ef914298c343fa39cccb1290aba48bf6
- https://github.com/zitadel/zitadel/commit/3c7d12834e32426416235b9e3374be0f4b9380b8
- https://github.com/zitadel/zitadel/commit/5c2526c98aafd1ba206be2fa4291b1d24c384f6d
- https://github.com/zitadel/zitadel/commit/8565d24fd8df5bd35294313cfbfcc2e15aea20e9
- https://github.com/zitadel/zitadel/commit/b0e71a81ef39667ce2a149ce037c1ca0edbe059d
- https://github.com/zitadel/zitadel/commit/fc1d415b8db5b8d481bb65206ce3fc944c0eecea
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.53.9
- https://github.com/zitadel/zitadel/releases/tag/v2.54.8
- https://github.com/zitadel/zitadel/releases/tag/v2.55.5
- https://github.com/zitadel/zitadel/releases/tag/v2.56.2
- https://github.com/zitadel/zitadel/releases/tag/v2.57.1
- https://github.com/zitadel/zitadel/releases/tag/v2.58.1
- https://pkg.go.dev/vuln/GO-2024-3014
