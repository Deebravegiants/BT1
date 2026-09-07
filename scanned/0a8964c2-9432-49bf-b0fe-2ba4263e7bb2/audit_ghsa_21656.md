# [M] Pivotal Concourse Open Redirect in Login Flow

## Summary
Severity: Medium
Advisory: GHSA-9689-rx4v-cqgc
CVE: CVE-2018-15798
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-9689-rx4v-cqgc
Type: github-advisory

## Affected
- Go: `github.com/concourse/concourse` — affected >=0 <5.2.8
- Go: `github.com/concourse/concourse` — affected >=5.3.0 <5.5.10
- Go: `github.com/concourse/concourse` — affected >=5.6.0 <5.8.1

## Details
Pivotal Concourse Release, versions 4.x prior to 4.2.2, login flow allows redirects to untrusted websites. A remote unauthenticated attacker could convince a user to click on a link using the oAuth redirect link with an untrusted website and gain access to that user's access token in Concourse.

### Specific Go Packages Affected
github.com/concourse/concourse/skymarshal/skyserver

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15798
- https://github.com/concourse/concourse/pull/5350/commits/38cb4cc025e5ed28764b4adc363a0bbf41f3c7cb
- https://github.com/concourse/concourse/blob/release/5.2.x/release-notes/v5.2.8.md
- https://pivotal.io/security/cve-2018-15798
