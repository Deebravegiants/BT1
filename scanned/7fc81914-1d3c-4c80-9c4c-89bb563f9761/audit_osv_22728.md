# [M] vim autocmd quickfix.c qf_update_buffer use after free

## Summary
Severity: Medium
Advisory: CVE-2022-3705
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-3705
Type: osv

## Details
A vulnerability was found in vim and classified as problematic. Affected by this issue is the function qf_update_buffer of the file quickfix.c of the component autocmd Handler. The manipulation leads to use after free. The attack may be launched remotely. Upgrading to version 9.0.0805 is able to address this issue. The name of the patch is d0fab10ed2a86698937e3c3fed2f10bd9bb5e731. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-212324.

## References
- https://support.apple.com/kb/HT213605
- https://vuldb.com/?id.212324
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3705.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4JCW33NOLMELTTTDJH7WGDIFJZ5YEEMK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GTBVD4J2SKVSWK4VBN5JP5OEVK6GDS3N/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JYEK5RNMH7MVQH6RPBKLSCCA6NMIKHDV/
- https://nvd.nist.gov/vuln/detail/CVE-2022-3705
- https://security.gentoo.org/glsa/202305-16
- https://security.netapp.com/advisory/ntap-20221223-0004/
- https://github.com/vim/vim/commit/d0fab10ed2a86698937e3c3fed2f10bd9bb5e731
- http://seclists.org/fulldisclosure/2023/Jan/19
- https://lists.debian.org/debian-lts-announce/2022/11/msg00009.html
