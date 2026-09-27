# [M] Unrestricted Upload of File with Dangerous Type in unisharp/laravel-filemanager

## Summary
Severity: Medium
Advisory: GHSA-f8x6-m9f5-ffp8
CVE: CVE-2021-23814
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-f8x6-m9f5-ffp8
Type: github-advisory

## Affected
- Packagist: `unisharp/laravel-filemanager` — affected >=0 <2.6.2

## Details
This affects the package unisharp/laravel-filemanager prior to version 2.6.2. The `upload()` function does not sufficiently validate the file type when uploading.

An attacker may be able to reproduce the following steps:
- Install a package with a web Laravel application.
- Navigate to the Upload window
- Upload an image file, then capture the request
- Edit the request contents with a malicious file (webshell)
- Enter the path of file uploaded on URL
- Remote Code Execution

**Note: Prevention for bad extensions can be done by using a whitelist in the config file(lfm.php). Corresponding document can be found in the [here](https://unisharp.github.io/laravel-filemanager/configfolder-categories).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23814
- https://github.com/UniSharp/laravel-filemanager/issues/1113#issuecomment-1812092975
- https://github.com/UniSharp/laravel-filemanager/commit/bd84899ce65a7f193e676dd8444e424fa50f64fa
- https://github.com/UniSharp/laravel-filemanager
- https://github.com/UniSharp/laravel-filemanager/blob/master/src/Controllers/UploadController.php#L26
- https://github.com/UniSharp/laravel-filemanager/blob/master/src/Controllers/UploadController.php%23L26
- https://snyk.io/vuln/SNYK-PHP-UNISHARPLARAVELFILEMANAGER-1567199
