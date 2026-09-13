# [H] CVE-2020-0432

## Summary
Severity: High
Advisory: CVE-2020-0432
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-17
Source: https://osv.dev/vulnerability/CVE-2020-0432
Type: osv

## Details
In skb_to_mamac of networking.c, there is a possible out of bounds write due to an integer overflow. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-143560807

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00021.html
- https://source.android.com/security/bulletin/pixel/2020-09-01
