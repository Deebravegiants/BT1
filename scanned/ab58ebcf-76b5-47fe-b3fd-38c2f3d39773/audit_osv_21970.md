# [M] CVE-2022-2056

## Summary
Severity: Medium
Advisory: CVE-2022-2056
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-06-30
Source: https://osv.dev/vulnerability/CVE-2022-2056
Type: osv

## Details
Divide By Zero error in tiffcrop in libtiff 4.4.0 allows attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit f3a5e010.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2056.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2056.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4TSS7MJ7OO7JO5BNKCRYSFU7UAYOKLA2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OXUMJXVEAYFWRO3U3YHKSULHIVDOLEQS/
- https://nvd.nist.gov/vuln/detail/CVE-2022-2056
- https://security.netapp.com/advisory/ntap-20220826-0001/
- https://www.debian.org/security/2023/dsa-5333
- https://gitlab.com/libtiff/libtiff/-/issues/415
- https://gitlab.com/libtiff/libtiff/-/merge_requests/346
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
