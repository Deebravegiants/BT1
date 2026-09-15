# [C] CVE-2021-43310

## Summary
Severity: Critical
Advisory: CVE-2021-43310
Aliases: GHSA-2m39-75g9-ff5r
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2021-43310
Type: osv

## Details
A vulnerability in Keylime before 6.3.0 allows an attacker to craft a request to the agent that resets the U and V keys as if the agent were being re-added to a verifier. This could lead to a remote code execution.

## References
- https://github.com/keylime/keylime/security/advisories/GHSA-2m39-75g9-ff5r
- https://seclists.org/oss-sec/2022/q1/101
