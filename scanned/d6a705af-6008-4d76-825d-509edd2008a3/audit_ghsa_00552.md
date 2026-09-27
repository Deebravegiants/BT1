# [C] Unrestricted Upload of File with Dangerous Type in mingsoft:ms-mcms

## Summary
Severity: Critical
Advisory: GHSA-c7c7-xm8g-xm36
CVE: CVE-2018-18830
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-11-01
Source: https://github.com/advisories/GHSA-c7c7-xm8g-xm36
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
An issue was discovered in com\mingsoft\basic\action\web\FileAction.java in MCMS 4.6.5. Since the upload interface does not verify the user login status, you can use this interface to upload files without setting a cookie. First, start an upload of JSP code with a .png filename, and then intercept the data packet. In the name parameter, change the suffix to jsp. In the response, the server returns the storage path of the file, which can be accessed to execute arbitrary JSP code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18830
- https://gitee.com/mingSoft/MCMS
- https://gitee.com/mingSoft/MCMS/issues/IO0IQ
- https://github.com/advisories/GHSA-c7c7-xm8g-xm36
