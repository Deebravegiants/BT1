# [M] Resource Exhaustion Denial of Service in http-proxy-agent 

## Summary
Severity: Medium
Advisory: GHSA-86wf-436m-h424
CVE: CVE-2019-10196
CWE: CWE-665
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-86wf-436m-h424
Type: github-advisory

## Affected
- npm: `http-proxy-agent` — affected >=0 <2.1.0

## Details
A flaw was found in http-proxy-agent, prior to version 2.1.0. It was discovered http-proxy-agent passes an auth option to the Buffer constructor without proper sanitization. This could result in a Denial of Service through the usage of all available CPU resources and data exposure through an uninitialized memory leak in setups where an attacker could submit typed input to the auth parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10196
- https://github.com/TooTallNate/node-http-proxy-agent/commit/b7b7cc793c3226aa83f820ce5c277e81862d32eb
- https://bugzilla.redhat.com/show_bug.cgi?id=1567245
- https://www.npmjs.com/advisories/607
