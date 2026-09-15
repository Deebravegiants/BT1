# [H] Sandbox Accounts for Events vulnerable to privilege escalation to read running events data

## Summary
Severity: High
Advisory: CVE-2023-51386
Aliases: GHSA-p7w3-j66h-m7mx
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-22
Source: https://osv.dev/vulnerability/CVE-2023-51386
Type: osv

## Details
Sandbox Accounts for Events provides multiple, temporary AWS accounts to a number of authenticated users simultaneously via a browser-based GUI. Authenticated users could potentially read data from the events table by sending request payloads to the events API, collecting information on planned events, timeframes, budgets and owner email addresses. This data access may allow users to get insights into upcoming events and join events which they have not been invited to. This issue has been patched in version 1.10.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51386.json
- https://github.com/awslabs/sandbox-accounts-for-events/security/advisories/GHSA-p7w3-j66h-m7mx
- https://nvd.nist.gov/vuln/detail/CVE-2023-51386
- https://github.com/awslabs/sandbox-accounts-for-events/commit/f30a0662f0a28734eb33c5868cccc1c319eb6e79
