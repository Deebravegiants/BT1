# [H] Improper Restriction of XML External Entity Reference in Dragonfly

## Summary
Severity: High
Advisory: CVE-2022-41967
Aliases: GHSA-6x3m-96qp-mmxv
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2022-12-27
Source: https://osv.dev/vulnerability/CVE-2022-41967
Type: osv

## Details
Dragonfly is a Java runtime dependency management library. Dragonfly v0.3.0-SNAPSHOT does not configure DocumentBuilderFactory to prevent XML external entity (XXE) attacks. This issue is patched in 0.3.1-SNAPSHOT. As a workaround, since Dragonfly only parses XML `SNAPSHOT` versions are being resolved, this vulnerability may be avoided by not trying to resolve `SNAPSHOT` versions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41967.json
- https://github.com/HyperaDev/Dragonfly/security/advisories/GHSA-6x3m-96qp-mmxv
- https://nvd.nist.gov/vuln/detail/CVE-2022-41967
- https://github.com/HyperaDev/Dragonfly/commit/9661375e1135127ca6cdb5712e978bec33cc06b3
