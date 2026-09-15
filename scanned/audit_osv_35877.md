# [C] CVE-2026-15971

## Summary
Severity: Critical
Advisory: CVE-2026-15971
Aliases: GHSA-h6rf-77vv-9mvj
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-15971
Type: osv

## Details
SGLang contains an RCE vulnerability when the optional dumper subsystem is enabled, allowing for a sandbox escape when DUMPER_SERVER_PORT is set, enabling code execution on inference requests.

## References
- https://thoughts.apoorvdayal.com/posts/sglang-disclosures/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15971.json
- https://github.com/sgl-project/sglang/security/advisories/GHSA-h6rf-77vv-9mvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-15971
