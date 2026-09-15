# [M] Juju affected by timing ownership claim attack on new external back-end secrets

## Summary
Severity: Medium
Advisory: GHSA-gfgr-6hrj-85ww
CVE: CVE-2026-32691
CWE: CWE-708
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-gfgr-6hrj-85ww
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=3.0.0 <3.6.19

## Details
A race condition in the secrets management subsystem of Juju versions 3.0.0 through 3.6.18 allows an authenticated unit agent to claim ownership of a newly initialized secret. Between generating a Juju Secret ID and creating the secret's first revision, an attacker authenticated as another unit agent can claim ownership of a known secret. This leads to the attacking unit being able to read the content of the initial secret revision.

### Impact
Between generating a Secret ID and creating the secret's first revision, an
attacker authenticated as another unit agent can claim ownership of a known
secret. This leads to the attacking unit being able to read the content of the
initial secret revision.

### Patches
3.6.19

## References
- https://github.com/juju/juju/security/advisories/GHSA-gfgr-6hrj-85ww
- https://nvd.nist.gov/vuln/detail/CVE-2026-32691
- https://github.com/juju/juju
