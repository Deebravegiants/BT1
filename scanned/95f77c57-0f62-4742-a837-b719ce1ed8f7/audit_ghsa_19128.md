# [M] Solon Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-x8q6-cchr-p7m6
CVE: CVE-2025-1584
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-02-23
Source: https://github.com/advisories/GHSA-x8q6-cchr-p7m6
Type: github-advisory

## Affected
- Maven: `org.noear:solon-web-staticfiles` — affected >=0 <3.0.9

## Details
A vulnerability classified as problematic was found in opensolon Solon up to 3.0.8. This vulnerability affects unknown code of the file solon-projects/solon-web/solon-web-staticfiles/src/main/java/org/noear/solon/web/staticfiles/StaticMappings.java. The manipulation leads to path traversal: '../filedir'. The attack can be initiated remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 3.0.9 is able to address this issue. The name of the patch is f46e47fd1f8455b9467d7ead3cdb0509115b2ef1. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1584
- https://github.com/opensolon/solon/issues/332
- https://github.com/opensolon/solon/issues/332#issue-2866229828
- https://github.com/opensolon/solon/issues/332#issuecomment-2674330700
- https://github.com/opensolon/solon/commit/f46e47fd1f8455b9467d7ead3cdb0509115b2ef1
- https://github.com/opensolon/solon
- https://vuldb.com/?ctiid.296560
- https://vuldb.com/?id.296560
- https://vuldb.com/?submit.504454
