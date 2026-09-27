# [M] JsonToObjectTransformer resolves the json__TypeId__ message header to an arbitrary class without an allow-list

## Summary
Severity: Medium
Advisory: CVE-2026-47856
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47856
Type: osv

## Details
Spring Integration's JSON to object conversion uses the json__TypeId__ header to choose the deserialization target type, and resolves that header value to a class with ClassUtils.forName and no type/package allow-list.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12
Spring Integration 5.5.21 and earlier

## References
- https://spring.io/security/cve-2026-47856
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47856.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47856
