# [H] CVE-2020-35981

## Summary
Severity: High
Advisory: CVE-2020-35981
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-35981
Type: osv

## Details
An issue was discovered in GPAC version 0.8.0 and 1.0.1. There is an invalid pointer dereference in the function SetupWriters() in isomedia/isom_store.c.

## References
- https://github.com/gpac/gpac/commit/dae9900580a8888969481cd72035408091edb11b
- https://github.com/gpac/gpac/issues/1659
