# [M] Remote command injection when using sendmail email transport

## Summary
Severity: Medium
Advisory: GHSA-wfrj-qqc2-83cm
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-wfrj-qqc2-83cm
Type: github-advisory

## Affected
- npm: `ghost` — affected >=0 <4.15.0

## Details
### Impact

Sites using the `sendmail` transport as part of their `mail` config are vulnerable to remote command injection due to a [vulnerability](https://github.com/advisories/GHSA-48ww-j4fc-435p) in the `nodemailer` dependency.

Ghost defaults to the `direct` transport so this is only exploitable if the `sendmail` transport is explicitly used.

### Patches

Fixed in 4.15.0, all sites should upgrade as soon as possible.

### Workarounds

* Use an alternative email transport as described in the [docs](https://ghost.org/docs/config/#mail). 

### For more information

If you have any questions or comments about this advisory:

* email us at security@ghost.org

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-wfrj-qqc2-83cm
- https://github.com/TryGhost/Ghost/commit/93e4b2eafd18bc8e4c17924e0824e73617e7940c
- https://github.com/TryGhost/Ghost
- https://github.com/advisories/GHSA-48ww-j4fc-435p
