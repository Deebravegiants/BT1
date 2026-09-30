# [H] CVE-2018-14438

## Summary
Severity: High
Advisory: CVE-2018-14438
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-20
Source: https://osv.dev/vulnerability/CVE-2018-14438
Type: osv

## Details
In Wireshark through 2.6.2, the create_app_running_mutex function in wsutil/file_util.c calls SetSecurityDescriptorDacl to set a NULL DACL, which allows attackers to modify the access control arbitrarily.

## References
- http://www.securityfocus.com/bid/104876
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14921
