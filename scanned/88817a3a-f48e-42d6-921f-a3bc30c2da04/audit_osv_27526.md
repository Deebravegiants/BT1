# [C] The Dataease datasource exists deserialization and arbitrary file read vulnerability

## Summary
Severity: Critical
Advisory: CVE-2024-23328
Aliases: GHSA-8x8q-p622-jf25
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-02-01
Source: https://osv.dev/vulnerability/CVE-2024-23328
Type: osv

## Details
Dataease is an open source data visualization analysis tool. A deserialization vulnerability exists in the DataEase datasource, which can be exploited to execute arbitrary code. The location of the vulnerability code is `core/core-backend/src/main/java/io/dataease/datasource/type/Mysql.java.` The blacklist of mysql jdbc attacks can be bypassed and attackers can further exploit it for deserialized execution or reading arbitrary files. This vulnerability is patched in 1.18.15 and 2.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23328.json
- https://github.com/dataease/dataease/security/advisories/GHSA-8x8q-p622-jf25
- https://nvd.nist.gov/vuln/detail/CVE-2024-23328
- https://github.com/dataease/dataease/commit/4128adf5fc4592b55fa1722a53b178967545d46a
- https://github.com/dataease/dataease/commit/bb540e6dc83df106ac3253f331066129a7487d1a
