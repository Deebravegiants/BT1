# [H] Metersphere is vulnerable to Path Injection.

## Summary
Severity: High
Advisory: CVE-2022-23512
Aliases: GHSA-5mwp-xw7p-5j27
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-23512
Type: osv

## Details
MeterSphere is a one-stop open source continuous testing platform. Versions prior to 2.4.1 are vulnerable to Path Injection in ApiTestCaseService::deleteBodyFiles which takes a user-controlled string id and passes it to ApiTestCaseService, which uses the user-provided value (testId) in new File(BODY_FILE_DIR + "/" + testId), being deleted later by file.delete(). By adding some camouflage parameters to the url, an attacker can target files on the server. The vulnerability has been fixed in v2.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23512.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-5mwp-xw7p-5j27
- https://nvd.nist.gov/vuln/detail/CVE-2022-23512
