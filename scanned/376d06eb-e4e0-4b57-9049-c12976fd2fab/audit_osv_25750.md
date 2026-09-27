# [H] libcue vulnerable to out-of-bounds array access

## Summary
Severity: High
Advisory: CVE-2023-43641
Aliases: GHSA-5982-x7hv-r9cj
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-10-09
Source: https://osv.dev/vulnerability/CVE-2023-43641
Type: osv

## Details
libcue provides an API for parsing and extracting data from CUE sheets. Versions 2.2.1 and prior are vulnerable to out-of-bounds array access. A user of the GNOME desktop environment can be exploited by downloading a cue sheet from a malicious webpage. Because the file is saved to `~/Downloads`, it is then automatically scanned by tracker-miners. And because it has a .cue filename extension, tracker-miners use libcue to parse the file. The file exploits the vulnerability in libcue to gain code execution. This issue is patched in version 2.3.0.

## References
- http://packetstormsecurity.com/files/176128/libcue-2.2.1-Out-Of-Bounds-Access.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/57JEYTRFG4PVGZZ7HIEFTX5I7OONFFMI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PGQOMFDBXGM3DOICCXKCUS76OTKTSPMN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XUS4HTNGGGUIFLYSKTODCRIOXLX5HGV3/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43641.json
- https://github.com/lipnitsk/libcue/security/advisories/GHSA-5982-x7hv-r9cj
- https://nvd.nist.gov/vuln/detail/CVE-2023-43641
- https://www.debian.org/security/2023/dsa-5524
- https://github.com/lipnitsk/libcue/commit/cfb98a060fd79dbc3463d85f0f29c3c335dfa0ea
- https://github.com/lipnitsk/libcue/commit/fdf72c8bded8d24cfa0608b8e97f2eed210a920e
- https://github.blog/2023-10-09-coordinated-disclosure-1-click-rce-on-gnome-cve-2023-43641/
