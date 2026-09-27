# [M] CVE-2021-0941

## Summary
Severity: Medium
Advisory: CVE-2021-0941
Aliases: A-154177719, PUB-A-154177719
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/CVE-2021-0941
Type: osv

## Details
In bpf_skb_change_head of filter.c, there is a possible out of bounds read due to a use after free. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-154177719References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2021-10-01
