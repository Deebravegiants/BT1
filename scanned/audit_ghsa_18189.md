# [M] SimStudioAI: A function in route.ts is vulnerable to Code Injection

## Summary
Severity: Medium
Advisory: GHSA-g4c9-f287-64xg
CVE: CVE-2025-10097
CWE: CWE-74, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-g4c9-f287-64xg
Type: github-advisory

## Affected
- npm: `simstudio` — affected >=0

## Details
A vulnerability was identified in SimStudioAI sim. This impacts an unknown function of the file apps/sim/app/api/function/execute/route.ts. The manipulation of the argument code leads to code injection. The attack is possible to be carried out remotely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10097
- https://github.com/simstudioai/sim/issues/961
- https://github.com/simstudioai/sim/issues/961#issuecomment-3215578979
- https://github.com/simstudioai/sim/pull/1149/commits/3f790867427275ebae3b3dc75cf1d93d912ac9ca
- https://github.com/simstudioai/sim
- https://vuldb.com/?ctiid.323058
- https://vuldb.com/?id.323058
- https://vuldb.com/?submit.644954
