# [M] nest allows a remote attacker to execute arbitrary code via the Content-Type header

## Summary
Severity: Medium
Advisory: GHSA-cj7v-w2c7-cp7c
CVE: CVE-2024-29409
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-03-14
Source: https://github.com/advisories/GHSA-cj7v-w2c7-cp7c
Type: github-advisory

## Affected
- npm: `@nestjs/common` — affected >=11.0.0-next.1 <11.0.16
- npm: `@nestjs/common` — affected >=0 <10.4.16

## Details
File Upload vulnerability in nestjs nest prior to v.11.0.16 allows a remote attacker to execute arbitrary code via the Content-Type header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29409
- https://github.com/nestjs/nest/issues/13311#issuecomment-1993839495
- https://github.com/nestjs/nest/issues/14876
- https://github.com/nestjs/nest/issues/14876#issuecomment-2796888038
- https://github.com/nestjs/nest/pull/14881
- https://gist.github.com/aydinnyunus/801342361584d1491c67a820a714f53f
- https://github.com/nestjs/nest
- https://github.com/nestjs/nest/blob/83a48b2c7396985144b7a6cd5d3bee1abb7c5d81/packages/common/pipes/file/file-type.validator.ts#L19
- https://github.com/nestjs/nest/releases/tag/v10.4.16
- https://github.com/nestjs/nest/releases/tag/v11.0.16
