# [H] CVE-2020-35979

## Summary
Severity: High
Advisory: CVE-2020-35979
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-35979
Type: osv

## Details
An issue was discovered in GPAC version 0.8.0 and 1.0.1. There is heap-based buffer overflow in the function gp_rtp_builder_do_avc() in ietf/rtp_pck_mpeg4.c.

## References
- https://github.com/gpac/gpac/commit/b15020f54aff24aaeb64b80771472be8e64a7adc
- https://github.com/gpac/gpac/issues/1662
