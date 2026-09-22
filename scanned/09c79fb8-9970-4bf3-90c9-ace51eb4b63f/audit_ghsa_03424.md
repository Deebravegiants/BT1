# [H] Denial of Service in get-ip-range

## Summary
Severity: High
Advisory: GHSA-6q4w-3wp4-q5wf
CVE: CVE-2021-27191
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-6q4w-3wp4-q5wf
Type: github-advisory

## Affected
- npm: `get-ip-range` — affected >=0 <4.0.0

## Details
The get-ip-range package before 4.0.0 for Node.js is vulnerable to denial of service (DoS) if the range is untrusted input. An attacker could send a large range (such as 128.0.0.0/1) that causes resource exhaustion. Update get-ip-range dependency to 4.0.0 or above.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27191
- https://github.com/JoeScho/get-ip-range/commit/98ca22b815c77273cbab259811ab0976118e13b6
- https://advisory.checkmarx.net/advisory/CX-2021-4304
- https://security.netapp.com/advisory/ntap-20210319-0002
- https://www.npmjs.com/package/get-ip-range
