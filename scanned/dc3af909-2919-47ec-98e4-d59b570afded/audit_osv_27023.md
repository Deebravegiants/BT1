# [H] Prevent timing attack for single-user password check

## Summary
Severity: High
Advisory: CVE-2024-0436
CVSS: 7.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2024-02-25
Source: https://osv.dev/vulnerability/CVE-2024-0436
Type: osv

## Details
Theoretically, it would be possible for an attacker to brute-force the password for an instance in single-user password protection mode via a timing attack given the linear nature of the `!==` used for comparison.

The risk is minified by the additional overhead of the request, which varies in a non-constant nature making the attack less reliable to execute

## References
- https://huntr.com/bounties/3e73cb96-c038-46a1-81b7-4d2215b36268
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0436.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0436
- https://github.com/mintplex-labs/anything-llm/commit/3c859ba3038121b67fb98e87dc52617fa27cbef0
