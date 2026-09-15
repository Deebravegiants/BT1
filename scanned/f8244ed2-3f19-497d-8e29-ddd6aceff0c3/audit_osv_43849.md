# [H] OpnForm Editable Submission Secret Derivation via Empty Hashids Salt

## Summary
Severity: High
Advisory: CVE-2026-75106
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75106
Type: osv

## Details
OpnForm derives editable-submission secrets from sequential row identifiers using Hashids with an empty default salt, allowing unauthenticated attackers to compute hashes for any submission. Attackers can read other respondents' full submission data through the submission-fetch endpoint or overwrite submissions by supplying predicted hashes to the answer endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75106.json
- https://github.com/OpnForm/OpnForm/releases/tag/v2.0.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-75106
- https://www.vulncheck.com/advisories/opnform-editable-submission-secret-derivation-via-empty-hashids-salt
- https://github.com/OpnForm/OpnForm/issues/1259
- https://github.com/OpnForm/OpnForm/commit/6c67ff0a9bc0ac27ae26b32b8e108a176f8161b1
- https://github.com/OpnForm/OpnForm
