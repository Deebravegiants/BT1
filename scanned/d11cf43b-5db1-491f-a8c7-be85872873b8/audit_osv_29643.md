# [M] Fides Webserver Authentication Timing-Based Username Enumeration Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-45052
Aliases: GHSA-2h46-8gf5-fmxv, PYSEC-2026-1331
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-45052
Type: osv

## Details
Fides is an open-source privacy engineering platform. Prior to version 2.44.0, a timing-based username enumeration vulnerability exists in Fides Webserver authentication. This vulnerability allows an unauthenticated attacker to determine the existence of valid usernames by analyzing the time it takes for the server to respond to login requests. The discrepancy in response times between valid and invalid usernames can be leveraged to enumerate users on the system. This vulnerability enables a timing-based username enumeration attack. An attacker can systematically guess and verify which usernames are valid by measuring the server's response time to authentication requests. This information can be used to conduct further attacks on authentication such as password brute-forcing and credential stuffing. The vulnerability has been patched in Fides version `2.44.0`. Users are advised to upgrade to this version or later to secure their systems against this threat. There are no workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45052.json
- https://github.com/ethyca/fides/security/advisories/GHSA-2h46-8gf5-fmxv
- https://nvd.nist.gov/vuln/detail/CVE-2024-45052
- https://github.com/ethyca/fides/commit/457b0e9df9f0d337133d6078bca6ed88bbc745f4
