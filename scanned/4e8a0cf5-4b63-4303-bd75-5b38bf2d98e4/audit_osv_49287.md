# [H] CVE-2018-9363

## Summary
Severity: High
Advisory: CVE-2018-9363
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-06
Source: https://osv.dev/vulnerability/CVE-2018-9363
Type: osv

## Details
In the hidp_process_report in bluetooth, there is an integer overflow. This could lead to an out of bounds write with no additional execution privileges needed. User interaction is not needed for exploitation. Product: Android Versions: Android kernel Android ID: A-65853588 References: Upstream kernel.

## References
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:2043
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://source.android.com/security/bulletin/2018-06-01
- https://usn.ubuntu.com/3797-1/
- https://usn.ubuntu.com/3797-2/
- https://usn.ubuntu.com/3820-2/
- https://usn.ubuntu.com/3820-1/
- https://usn.ubuntu.com/3820-3/
- https://usn.ubuntu.com/3822-1/
- https://usn.ubuntu.com/3822-2/
- https://www.debian.org/security/2018/dsa-4308
