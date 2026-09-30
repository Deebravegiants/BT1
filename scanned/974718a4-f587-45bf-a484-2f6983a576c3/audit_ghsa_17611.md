# [M] HAX CMS vulnerable to Local File Inclusion via saveOutline API Location Parameter

## Summary
Severity: Medium
Advisory: GHSA-hxrr-x32w-cg8g
CVE: CVE-2025-49138
CWE: CWE-22, CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-hxrr-x32w-cg8g
Type: github-advisory

## Affected
- Packagist: `elmsln/haxcms` — affected >=0 <11.0.0

## Details
### Summary
An authenticated Local File Inclusion (LFI) vulnerability in the HAXCMS saveOutline endpoint allows a low-privileged user to read arbitrary files on the server by manipulating the location field written into site.json. This enables attackers to exfiltrate sensitive system files such as /etc/passwd, application secrets, or configuration files accessible to the web server (www-data).

### Details
The vulnerability stems from the way the HAXCMS backend handles the location field in the site's outline. When a user sends a POST request to /system/api/saveOutline, the backend stores the provided location value directly into the site.json file associated with the site, without validating or sanitizing the input.

Later the location parameter is interpreted by the CMS like in[ HAXCMSSite.php line 1248](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/HAXCMSSite.php#L1248) to resolve and load the content for a given node. If the location field contains a relative path like ../../../etc/passwd, the application will attempt to read and render that file.

### PoC
1. Authenticate to the CMS and retrieve the JWT and CSRF token.

2. Issue a POST request to /system/api/saveOutline with the path traversal injection via the location parameter :

<img width="839" alt="LFI" src="https://github.com/user-attachments/assets/91b1bb7f-9248-40d2-81fc-f839beb4d39c" />

3. Curl the website root to see the file contents.

![passwd](https://github.com/user-attachments/assets/21adbb00-8e57-48f6-b1e9-f5b03ec65b55)


### Impact
This is an authenticated Local File Inclusion (LFI) vulnerability, via the location parameter the attacker can read any file on the filesystem that is accessible by the www-data user.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-hxrr-x32w-cg8g
- https://nvd.nist.gov/vuln/detail/CVE-2025-49138
- https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/HAXCMSSite.php#L1248
- https://github.com/haxtheweb/issues
