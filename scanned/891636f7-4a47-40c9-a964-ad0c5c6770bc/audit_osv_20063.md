# [M] CVE-2021-30015

## Summary
Severity: Medium
Advisory: CVE-2021-30015
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-30015
Type: osv

## Details
There is a Null Pointer Dereference in function filter_core/filter_pck.c:gf_filter_pck_new_alloc_internal in GPAC 1.0.1. The pid comes from function av1dmx_parse_flush_sample, the ctx.opid maybe NULL. The result is a crash in gf_filter_pck_new_alloc_internal.

## References
- https://github.com/gpac/gpac/commit/13dad7d5ef74ca2e6fe4010f5b03eb12e9bbe0ec
- https://github.com/gpac/gpac/issues/1719
