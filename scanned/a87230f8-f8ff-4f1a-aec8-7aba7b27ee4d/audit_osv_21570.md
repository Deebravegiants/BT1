# [M] CVE-2021-44141

## Summary
Severity: Medium
Advisory: CVE-2021-44141
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-02-21
Source: https://osv.dev/vulnerability/CVE-2021-44141
Type: osv

## Details
All versions of Samba prior to 4.15.5 are vulnerable to a malicious client using a server symlink to determine if a file or directory exists in an area of the server file system not exported under the share definition. SMB1 with unix extensions has to be enabled in order for this attack to succeed.

## References
- https://security.gentoo.org/glsa/202309-06
- https://www.samba.org/samba/security/CVE-2021-44141.html
