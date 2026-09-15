# [M] CVE-2021-40944

## Summary
Severity: Medium
Advisory: CVE-2021-40944
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-06-28
Source: https://osv.dev/vulnerability/CVE-2021-40944
Type: osv

## Details
In GPAC MP4Box 1.1.0, there is a Null pointer reference in the function gf_filter_pid_get_packet function in src/filter_core/filter_pid.c:5394, as demonstrated by GPAC. This can cause a denial of service (DOS).

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1906
