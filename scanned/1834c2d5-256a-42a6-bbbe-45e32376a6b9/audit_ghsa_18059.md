# [H] hippo4j Includes Hard Coded Secret Key in JWT Creation

## Summary
Severity: High
Advisory: GHSA-48cg-9c55-j2q7
CVE: CVE-2025-51606
CWE: CWE-798
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-48cg-9c55-j2q7
Type: github-advisory

## Affected
- Maven: `cn.hippo4j:hippo4j-core` — affected >=1.0.0

## Details
hippo4j 1.0.0 to 1.5.0, uses a hard-coded secret key in its JWT (JSON Web Token) creation. This allows attackers with access to the source code or compiled binary to forge valid access tokens and impersonate any user, including privileged ones such as "admin". The vulnerability poses a critical security risk in systems where authentication and authorization rely on the integrity of JWTs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-51606
- https://github.com/ShenxiuSec/cve-proofs/blob/main/POC-20250610-01.md
- https://github.com/opengoofy/hippo4j
- https://github.com/opengoofy/hippo4j/blob/7d78be3cab526501ad876495862f4cec108da2af/threadpool/server/auth/src/main/java/cn/hippo4j/auth/security/JwtTokenManager.java#L51
