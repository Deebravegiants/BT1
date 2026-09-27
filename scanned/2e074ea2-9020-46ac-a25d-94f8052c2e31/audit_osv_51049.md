# [M] CVE-2021-0920

## Summary
Severity: Medium
Advisory: CVE-2021-0920
Aliases: A-196926917, ASB-A-196926917
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-0920
Type: osv

## Details
In unix_scm_to_skb of af_unix.c, there is a possible use after free bug due to a race condition. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-196926917References: Upstream kernel

## References
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://source.android.com/security/bulletin/2021-11-01
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-0920
