# [M] Dapr API Token Exposure

## Summary
Severity: Medium
Advisory: GHSA-284c-x8m7-9w5h
CVE: CVE-2024-35223
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-22
Source: https://github.com/advisories/GHSA-284c-x8m7-9w5h
Type: github-advisory

## Affected
- Go: `github.com/dapr/dapr` — affected >=1.13.0 <1.13.3

## Details
### **Summary**

A vulnerability has been found in Dapr that causes a leak of the application token of the invoker app to the invoked app when using Dapr as a gRPC proxy for remote service invocation. This issue arises because Dapr sends the app token of the invoker app instead of the app token of the invoked app.

Users who leverage Dapr for gRPC proxy service invocation and are using the app API token feature are encouraged to upgrade Dapr to version [1.13.3](https://github.com/dapr/dapr/releases/tag/v1.13.3). 

### Impact

This vulnerability impacts Dapr users who use Dapr as a gRPC proxy for remote service invocation as well as the [Dapr App API token](https://docs.dapr.io/operations/security/app-api-token/) functionality. An attacker could exploit this vulnerability to gain access to the app token of the invoker app, potentially compromising security and authentication mechanisms.

### Patches

The issue has been fixed in Dapr version [1.13.3](https://github.com/dapr/dapr/releases/tag/v1.13.3).

### Details

Dapr uses two types of tokens for authentication:

- `APP_API_TOKEN`: Used by Dapr to authenticate to the app.
- `DAPR_API_TOKEN`: Used by the app to authenticate to Dapr.

Dapr uses the `dapr-api-token` metadata in gRPC calls (or header, for HTTP calls) for authentication.

- In communication from dapr to the app, the `dapr-api-token` metadata field will carry the  `APP_API_TOKEN`.
- In communication from the app to daprd, the `dapr-api-token` metadata field will carry the  `DAPR_API_TOKEN`.

Before version 1.13.0, the `APP_API_TOKEN` was not being sent to the invoked app for authentication, as reported in [this issue](https://github.com/dapr/dapr/issues/7344). Instead, Dapr was incorrectly using the same `DAPR_API_TOKEN` that the invoker app had passed to Dapr. This was addressed in [PR #7404](https://github.com/dapr/dapr/pull/7404), but the fix only worked for self-invocation scenarios.

When Dapr needed to communicate with another instance, it would mistakenly include the `APP_API_TOKEN` of the invoker app in the request. This behavior is incorrect, app tokens should never be included in requests between Dapr sidecars. This vulnerability allows the receiving app to see the app token of the invoker app, leading to potential misuse and security breaches.

The vulnerability is addressed by ensuring that Dapr uses the correct app token (of the invoked app) during gRPC proxy service invocation.

### References

- https://docs.dapr.io/operations/security/app-api-token/
- https://github.com/dapr/dapr/issues/7344
- https://github.com/dapr/dapr/pull/7404 

### Credits

Thanks to [Benjamin Delay](mailto:benjamin.delay@gmail.com) for reporting this issue.

## References
- https://github.com/dapr/dapr/security/advisories/GHSA-284c-x8m7-9w5h
- https://nvd.nist.gov/vuln/detail/CVE-2024-35223
- https://github.com/dapr/dapr/issues/7344
- https://github.com/dapr/dapr/pull/7404
- https://github.com/dapr/dapr/commit/e0591e43d0cdfd30a2f2960dce5d9892dc98bc2c
- https://github.com/dapr/dapr
- https://github.com/dapr/dapr/releases/tag/v1.13.3
