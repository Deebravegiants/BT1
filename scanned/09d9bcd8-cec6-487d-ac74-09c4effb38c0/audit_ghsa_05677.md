# [M] go-tuf affected by client DoS via malformed server response

## Summary
Severity: Medium
Advisory: GHSA-846p-jg2w-w324
CVE: CVE-2026-23991
CWE: CWE-617, CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-846p-jg2w-w324
Type: github-advisory

## Affected
- Go: `github.com/theupdateframework/go-tuf/v2` — affected >=0 <2.3.1

## Details
# Security Disclosure: Client DoS via malformed server response

## Summary

If the TUF repository (or any of its mirrors) returns invalid TUF metadata JSON (valid JSON but not well formed TUF metadata), the client will panic _during parsing_, causing a DoS. The panic happens before any signature is validated. This means that a compromised repository/mirror/cache can DoS clients without having access to any signing key.

## Impact 

Client crashes upon receiving and parsing malformed TUF metadata. This can cause long running services to enter an restart/crash loop.

## Workarounds

None currently. 

## Affected code

The `metadata.checkType` function did not properly type assert the (untrusted) input causing it to panic on malformed data.

## References
- https://github.com/theupdateframework/go-tuf/security/advisories/GHSA-846p-jg2w-w324
- https://nvd.nist.gov/vuln/detail/CVE-2026-23991
- https://github.com/theupdateframework/go-tuf/commit/73345ab6b0eb7e59d525dac17a428f043074cef6
- https://github.com/theupdateframework/go-tuf
- https://github.com/theupdateframework/go-tuf/releases/tag/v2.3.1
