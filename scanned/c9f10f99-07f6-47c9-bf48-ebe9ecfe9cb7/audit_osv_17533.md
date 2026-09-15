# [H] CVE-2020-15957

## Summary
Severity: High
Advisory: CVE-2020-15957
Aliases: GHSA-5m5q-3qw2-3xf3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-07-30
Source: https://osv.dev/vulnerability/CVE-2020-15957
Type: osv

## Details
An issue was discovered in DP3T-Backend-SDK before 1.1.1 for Decentralised Privacy-Preserving Proximity Tracing (DP3T). When it is configured to check JWT before uploading/publishing keys, it is possible to skip the signature check by providing a JWT token with alg=none.

## References
- https://github.com/DP-3T/dp3t-sdk-backend/compare/v1.0.4...v1.1.0
- https://github.com/dp-3T/dp3t-sdk-backend
- https://github.com/DP-3T/dp3t-sdk-backend/security/advisories/GHSA-5m5q-3qw2-3xf3
