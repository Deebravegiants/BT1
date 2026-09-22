# [H] Moby has AuthZ plugin bypass when provided oversized request bodies

## Summary
Severity: High
Advisory: GHSA-x744-4wpc-v9h2
CVE: CVE-2026-34040
CWE: CWE-863, CWE-288
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-x744-4wpc-v9h2
Type: github-advisory

## Affected
- Go: `github.com/moby/moby` — affected >=0 <29.3.1
- Go: `github.com/moby/moby/v2` — affected >=0 <2.0.0-beta.8

## Details
## Summary

A security vulnerability has been detected that allows attackers to bypass [authorization plugins (AuthZ)](https://docs.docker.com/engine/extend/plugins_authorization/) under specific circumstances. The base likelihood of this being exploited is low.

This is an incomplete fix for [CVE-2024-41110](https://github.com/moby/moby/security/advisories/GHSA-v23v-6jw2-98fq).

## Impact

**If you don't use AuthZ plugins, you are not affected.**

Using a specially-crafted API request, an attacker could make the Docker daemon forward the request to an authorization plugin without the body. The authorization plugin may allow a request which it would have otherwise denied if the body had been forwarded to it.

Anyone who depends on authorization plugins that introspect the request body to make access control decisions is potentially impacted.

## Workarounds

If unable to update immediately:
- Avoid using AuthZ plugins that rely on request body inspection for security decisions.
- Restrict access to the Docker API to trusted parties, following the principle of least privilege.

## Credits

- 1seal / Oleh Konko ([@1seal](https://github.com/1seal))
- Cody (c@wormhole.guru)
- Asim Viladi Oglu Manizada (@manizada)

## Resources

- [CVE-2024-41110 / GHSA-v23v-6jw2-98fq](https://github.com/moby/moby/security/advisories/GHSA-v23v-6jw2-98fq)

## References
- https://github.com/moby/moby/security/advisories/GHSA-v23v-6jw2-98fq
- https://github.com/moby/moby/security/advisories/GHSA-x744-4wpc-v9h2
- https://nvd.nist.gov/vuln/detail/CVE-2026-34040
- https://github.com/moby/moby/commit/e89edb19ad7de0407a5d31e3111cb01aa10b5a38
- https://docs.docker.com/engine/extend/plugins_authorization
- https://github.com/moby/moby
- https://github.com/moby/moby/releases/tag/docker-v29.3.1
