# [M] Cleartext Transmission of Sensitive Information in moment-timezone

## Summary
Severity: Medium
Advisory: GHSA-v78c-4p63-2j6c
CWE: CWE-319
Ecosystem: npm
Published: 2022-08-30
Source: https://github.com/advisories/GHSA-v78c-4p63-2j6c
Type: github-advisory

## Affected
- npm: `moment-timezone` — affected >=0.1.0 <0.5.35

## Details
### Impact

* if Alice uses `grunt data` (or `grunt release`) to prepare a custom-build, moment-timezone with the latest tzdata from IANA's website
* and Mallory intercepts the request to IANA's unencrypted ftp server, Mallory can serve data which might exploit further stages of the moment-timezone tzdata pipeline, or potentially produce a tainted version of moment-timezone (practicality of such attacks is not proved)

### Patches
Problem has been patched in version 0.5.35, patch should be applicable with minor modifications to all affected versions. The patch includes changing the FTP endpoint with an HTTPS endpoint.

### Workarounds
Specify the exact version of tzdata (like `2014d`, full command being `grunt data:2014d`, then run the rest of the release tasks by hand), or just apply the patch before issuing the grunt command.

## References
- https://github.com/moment/moment-timezone/security/advisories/GHSA-v78c-4p63-2j6c
- https://github.com/moment/moment-timezone/commit/7915ac567ab19700e44ad6b5d8ef0b85e48a9e75
- https://github.com/moment/moment-timezone
