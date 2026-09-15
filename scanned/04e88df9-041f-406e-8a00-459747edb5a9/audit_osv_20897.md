# [C] CVE-2021-38173

## Summary
Severity: Critical
Advisory: CVE-2021-38173
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-07
Source: https://osv.dev/vulnerability/CVE-2021-38173
Type: osv

## Details
Btrbk before 0.31.2 allows command execution because of the mishandling of remote hosts filtering SSH commands using ssh_filter_btrbk.sh in authorized_keys.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BP2T32JMENJFRP2HWXR7FTTZVRTTPECL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LM7GLTUN5YS4KE2RNBX732EAMVVGNEX3/
- https://github.com/digint/btrbk/blob/master/ChangeLog
- https://lists.debian.org/debian-lts-announce/2021/09/msg00002.html
- https://github.com/digint/btrbk/commit/58212de771c381cd4fa05625927080bf264e9584
