# [C] Path traversal and code execution via prototype vulnerability

## Summary
Severity: Critical
Advisory: GHSA-vh2g-6c4x-5hmp
CVE: CVE-2023-26045
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-vh2g-6c4x-5hmp
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=2.5.0 <2.8.7

## Details
### Impact
Due to the use of the [object destructuring assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment) syntax in the user export code path, combined with a path traversal vulnerability, a specially crafted payload could invoke the user export logic to arbitrarily execute javascript files on the local disk.

### Patches
Patched in v2.8.7

### Workarounds
Site maintainers can cherry pick ec58700f6dff8e5b4af1544f6205ec362b593092 into their codebase to patch the exploit.

## References
- https://github.com/NodeBB/NodeBB/security/advisories/GHSA-vh2g-6c4x-5hmp
- https://nvd.nist.gov/vuln/detail/CVE-2023-26045
- https://github.com/NodeBB/NodeBB/commit/ec58700f6dff8e5b4af1544f6205ec362b593092
- https://github.com/NodeBB/NodeBB
- https://security.netapp.com/advisory/ntap-20230831-0004
