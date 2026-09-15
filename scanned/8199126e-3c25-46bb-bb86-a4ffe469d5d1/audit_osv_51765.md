# [M] CVE-2021-39711

## Summary
Severity: Medium
Advisory: CVE-2021-39711
Aliases: A-154175781, PUB-A-154175781
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-39711
Type: osv

## Details
In bpf_prog_test_run_skb of test_run.c, there is a possible out of bounds read due to Incorrect Size Value. This could lead to local information disclosure with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-154175781References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2022-03-01
- https://source.android.com/security/bulletin/pixel/2022-03-01
