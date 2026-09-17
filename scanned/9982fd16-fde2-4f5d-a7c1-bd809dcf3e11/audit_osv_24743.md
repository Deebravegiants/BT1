# [H] Authenticate Remote Code Execution in Pluck CMS

## Summary
Severity: High
Advisory: CVE-2023-25828
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-25828
Type: osv

## Details
Pluck CMS is vulnerable to an authenticated remote code execution (RCE) vulnerability through its “albums” module. Albums are used to create collections of images that can be inserted into web pages across the site. Albums allow the upload of various filetypes, which undergo a normalization process before being available on the site. Due to lack of file extension validation, it is possible to upload a crafted JPEG payload containing an embedded PHP web-shell. An attacker may navigate to it directly to achieve RCE on the underlying web server. Administrator credentials for the Pluck CMS web interface are required to access the albums module feature, and are thus required to exploit this vulnerability. CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H/E:P/RL:O/RC:C (8.2 High)

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25828.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25828
- https://github.com/pluck-cms/pluck
- https://www.synopsys.com/blogs/software-security/pluck-cms-vulnerability/
