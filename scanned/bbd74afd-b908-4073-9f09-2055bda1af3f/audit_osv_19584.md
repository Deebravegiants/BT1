# [M] CVE-2021-22255

## Summary
Severity: Medium
Advisory: CVE-2021-22255
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-20
Source: https://osv.dev/vulnerability/CVE-2021-22255
Type: osv

## Details
SSRF in URL file upload in Baserow <1.1.0 allows remote authenticated users to retrieve files from the internal server network exposed over HTTP by inserting an internal address.

## References
- https://baserow.io/blog/march-2021-release-of-baserow
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22255.json
- https://gitlab.com/bramw/baserow/-/issues/370
