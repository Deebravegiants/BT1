# [H] Dapr: Service Invocation path traversal ACL bypass

## Summary
Severity: High
Advisory: GHSA-85gx-3qv6-4463
CVE: CVE-2026-41491
CWE: CWE-22, CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-85gx-3qv6-4463
Type: github-advisory

## Affected
- Go: `github.com/dapr/dapr` — affected >=1.17.0-rc.1 <1.17.5
- Go: `github.com/dapr/dapr` — affected >=1.16.0-rc.1 <1.16.14
- Go: `github.com/dapr/dapr` — affected >=1.3.0 <1.15.14

## Details
### Summary

A vulnerability has been found in Dapr that allows bypassing access control policies for service invocation using reserved URL characters and path traversal sequences in method paths. The ACL normalized the method path independently from the dispatch layer, so the ACL evaluated one path while the target application received a different one.

Users who have configured access control policies for service invocation are strongly encouraged to upgrade Dapr to the respective patch version `1.17.5`, `1.16.14`, and `1.15.14`.

### Impact

This vulnerability impacts Dapr users who have configured access control policies for service invocation. An attacker who can reach the Dapr HTTP or gRPC API could:

- Use encoded path traversal (ex: `admin%2F..%2Fpublic`) to reach an allowed path while the method started from a denied prefix.
- Use encoded fragment (`%23`) or query (`%3F`) characters to cause the ACL to evaluate a different path than what was delivered to the target application.

### Patches

Users should upgrade immediately to their respective Dapr version `1.17.5`, `1.16.14`, and `1.15.14`.

### Details

Dapr supports access control policies for service invocation, which allow operators to restrict which methods an application is permitted to call on a target app. When a request arrives, Dapr evaluates the method path against the configured policy before dispatching to the target.

Prior to this fix, the ACL and the dispatch layer normalized the method path independently. The ACL used `purell.NormalizeURLString`, which decoded `%XX` sequences, resolved `../`, and stripped `#` and `?` as URL delimiters. The dispatch layer used the raw method string. This mismatch meant the ACL authorized one path while the target application received a different one.

For example, a method of `admin%2F..%2Fpublic` was normalized by the ACL to public (allowed), but the target application received `admin/../public`. 

The gRPC API was the more dangerous vector because gRPC passes method strings raw — `#`, `?`, `../`, and control characters were all delivered literally with no client-side sanitization.

### References

[This PR](https://github.com/dapr/dapr/pull/9589) signaled to us about the CVE, special thanks to @dbconfession78 for the efforts here and the original PR.

## References
- https://github.com/dapr/dapr/security/advisories/GHSA-85gx-3qv6-4463
- https://nvd.nist.gov/vuln/detail/CVE-2026-41491
- https://github.com/dapr/dapr/pull/9589
- https://github.com/dapr/dapr
