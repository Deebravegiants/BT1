# [M] CVE-2022-1056

## Summary
Severity: Medium
Advisory: CVE-2022-1056
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-28
Source: https://osv.dev/vulnerability/CVE-2022-1056
Type: osv

## Details
Out-of-bounds Read error in tiffcrop in libtiff 4.3.0 allows attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 46dc8fcd.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1056.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1056.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1056
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20221228-0008/
- https://gitlab.com/libtiff/libtiff/-/issues/391
- https://gitlab.com/libtiff/libtiff/-/merge_requests/307
