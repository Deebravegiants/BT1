# [M] Github.com/go-viper/mapstructure/v2: go-viper's mapstructure may leak sensitive information in logs in github.com/go-viper/mapstructure

## Summary
Severity: Medium
Advisory: CVE-2025-11065
Aliases: GHSA-2464-8j7c-4cjm, GO-2025-3900
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2025-11065
Type: osv

## Details
A flaw was found in github.com/go-viper/mapstructure/v2, in the field processing component using mapstructure.WeakDecode. This vulnerability allows information disclosure through detailed error messages that may leak sensitive input values via malformed user-supplied data processed in security-critical contexts.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/go-viper/mapstructure/
- https://access.redhat.com/security/cve/CVE-2025-11065
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11065.json
- https://github.com/go-viper/mapstructure/security/advisories/GHSA-2464-8j7c-4cjm
- https://nvd.nist.gov/vuln/detail/CVE-2025-11065
- https://bugzilla.redhat.com/show_bug.cgi?id=2391829
- https://github.com/go-viper/mapstructure/commit/742921c9ba2854d27baa64272487fc5075d2c39c
