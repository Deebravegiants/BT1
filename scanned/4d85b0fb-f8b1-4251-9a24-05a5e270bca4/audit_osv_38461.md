# [M] Zip Slip Path Traversal in quarkus-openapi-generator ApicurioCodegenWrapper class

## Summary
Severity: Medium
Advisory: CVE-2026-40180
Aliases: GHSA-jx2w-vp7f-456q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-40180
Type: osv

## Details
Quarkus OpenAPI Generator is Quarkus' extensions for generation of Rest Clients and server stubs generation. Prior to 2.16.0 and 2.15.0-lts, the unzip() method in ApicurioCodegenWrapper.java extracts ZIP entries without validating that the resolved file path stays within the intended output directory. At line 101, the destination is constructed as new File(toOutputDir, entry.getName()) and the content is written immediately. A malicious ZIP archive containing entries with path traversal sequences (e.g., ../../malicious.java) would write files outside the target directory. This vulnerability is fixed in 2.16.0 and 2.15.0-lts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40180.json
- https://github.com/quarkiverse/quarkus-openapi-generator/security/advisories/GHSA-jx2w-vp7f-456q
- https://nvd.nist.gov/vuln/detail/CVE-2026-40180
- https://github.com/quarkiverse/quarkus-openapi-generator/commit/08b406414ff30ed192e86c7fa924e57565534ff0
- https://github.com/quarkiverse/quarkus-openapi-generator/commit/e2a9c629a3df719abc74569a3795c265fd0e1239
