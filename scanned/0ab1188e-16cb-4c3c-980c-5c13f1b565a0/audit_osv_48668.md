# [H] CVE-2018-10893

## Summary
Severity: High
Advisory: CVE-2018-10893
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-11
Source: https://osv.dev/vulnerability/CVE-2018-10893
Type: osv

## Details
Multiple integer overflow and buffer overflow issues were discovered in spice-client's handling of LZ compressed frames. A malicious server could cause the client to crash or, potentially, execute arbitrary code.

## References
- https://access.redhat.com/errata/RHSA-2019:2229
- https://access.redhat.com/errata/RHSA-2020:0471
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10893
- https://lists.freedesktop.org/archives/spice-devel/2018-July/044489.html
