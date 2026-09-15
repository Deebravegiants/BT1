# [M] CVE-2019-16986

## Summary
Severity: Medium
Advisory: CVE-2019-16986
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-10-21
Source: https://osv.dev/vulnerability/CVE-2019-16986
Type: osv

## Details
In FusionPBX up to v4.5.7, the file resources\download.php uses an unsanitized "f" variable coming from the URL, which takes any pathname and allows a download of it. (resources\secure_download.php is also affected.)

## References
- https://resp3ctblog.wordpress.com/2019/10/19/fusionpbx-path-traversal-2/
- https://github.com/fusionpbx/fusionpbx/commit/9482d9ee0e4287df21339be4276125e38e048951
- https://github.com/fusionpbx/fusionpbx/commit/9c61191049c949e01f99ea1fbab1feb44709e108
