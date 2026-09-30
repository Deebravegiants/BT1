# [M] AnythingLLM Vulnerable to Username Enumeration w/ Password Recovery

## Summary
Severity: Medium
Advisory: CVE-2026-21484
Aliases: GHSA-47vr-w3vm-69ch
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-03
Source: https://osv.dev/vulnerability/CVE-2026-21484
Type: osv

## Details
AnythingLLM is an application that turns pieces of content into context that any LLM can use as references during chatting. Prior to commit e287fab56089cf8fcea9ba579a3ecdeca0daa313, the password recovery endpoint returns different error messages depending on whether a username exists, so enabling username enumeration. Commit e287fab56089cf8fcea9ba579a3ecdeca0daa313 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21484.json
- https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-47vr-w3vm-69ch
- https://nvd.nist.gov/vuln/detail/CVE-2026-21484
- https://github.com/Mintplex-Labs/anything-llm/commit/e287fab56089cf8fcea9ba579a3ecdeca0daa313
