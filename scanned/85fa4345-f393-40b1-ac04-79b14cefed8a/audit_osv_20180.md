# [M] CVE-2021-31920

## Summary
Severity: Medium
Advisory: CVE-2021-31920
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2021-31920
Type: osv

## Details
Istio before 1.8.6 and 1.9.x before 1.9.5 has a remotely exploitable vulnerability where an HTTP request path with multiple slashes or escaped slash characters (%2F or %5C) could potentially bypass an Istio authorization policy when path based authorization rules are used.

## References
- https://istio.io/latest/news/security/istio-security-2021-005/
