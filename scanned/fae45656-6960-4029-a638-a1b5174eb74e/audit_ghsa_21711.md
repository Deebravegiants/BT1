# [M] jQuery-Upload-File XSS in fileNameStr

## Summary
Severity: Medium
Advisory: GHSA-43x9-7hfv-mxrf
CVE: CVE-2021-37504
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-26
Source: https://github.com/advisories/GHSA-43x9-7hfv-mxrf
Type: github-advisory

## Affected
- npm: `jquery-file-upload` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability in the fileNameStr parameter of jQuery-Upload-File v4.0.11 allows attackers to execute arbitrary web scripts or HTML via a crafted file with a Javascript payload in the file name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37504
- https://github.com/hayageek/jquery-upload-file
- https://github.com/hayageek/jquery-upload-file/blob/master/js/jquery.uploadfile.js#L469
