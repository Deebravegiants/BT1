# [H] dd-trace-cpp malformed unicode header values may cause crash

## Summary
Severity: High
Advisory: CVE-2024-38525
Aliases: GHSA-rf3p-mg22-qv6w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/CVE-2024-38525
Type: osv

## Details
dd-trace-cpp is the Datadog distributed tracing for C++. When the library fails to extract trace context due to malformed unicode, it logs the list of audited headers and their values using the `nlohmann` JSON library. However, due to the way the JSON library is invoked, it throws an uncaught exception, which results in a crash. This vulnerability has been patched in version 0.2.2.

## References
- https://github.com/DataDog/dd-trace-cpp/releases/tag/v0.2.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38525.json
- https://github.com/DataDog/dd-trace-cpp/security/advisories/GHSA-rf3p-mg22-qv6w
- https://nvd.nist.gov/vuln/detail/CVE-2024-38525
