# [M] jLEMS JUtil.java unpackJar path traversal

## Summary
Severity: Medium
Advisory: CVE-2022-4583
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-12-17
Source: https://osv.dev/vulnerability/CVE-2022-4583
Type: osv

## Details
A vulnerability was found in jLEMS. It has been declared as critical. Affected by this vulnerability is the function unpackJar of the file src/main/java/org/lemsml/jlems/io/util/JUtil.java. The manipulation leads to path traversal. The attack can be launched remotely. The name of the patch is 8c224637d7d561076364a9e3c2c375daeaf463dc. It is recommended to apply a patch to fix this issue. The identifier VDB-216169 was assigned to this vulnerability.

## References
- https://vuldb.com/?id.216169
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4583.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4583
- https://github.com/LEMS/jLEMS/commit/8c224637d7d561076364a9e3c2c375daeaf463dc
- https://github.com/LEMS/jLEMS/pull/103
