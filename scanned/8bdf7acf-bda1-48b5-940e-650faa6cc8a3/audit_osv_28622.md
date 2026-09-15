# [H] Denial of Service (DoS) Vulnerability in mintplex-labs/anything-llm

## Summary
Severity: High
Advisory: CVE-2024-3569
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-3569
Type: osv

## Details
A Denial of Service (DoS) vulnerability exists in the mintplex-labs/anything-llm repository when the application is running in 'just me' mode with a password. An attacker can exploit this vulnerability by making a request to the endpoint using the [validatedRequest] middleware with a specially crafted 'Authorization:' header. This vulnerability leads to uncontrolled resource consumption, causing a DoS condition.

## References
- https://huntr.com/bounties/619e13bd-b723-4727-9ccb-5099d698432e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3569.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3569
- https://github.com/mintplex-labs/anything-llm/commit/efe9dfa5e3550d12abd34d06ab7f8fbcf2206cfa
