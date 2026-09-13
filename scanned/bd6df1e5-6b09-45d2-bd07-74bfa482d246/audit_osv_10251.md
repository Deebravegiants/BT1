# [C] CVE-2017-14608

## Summary
Severity: Critical
Advisory: CVE-2017-14608
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-09-20
Source: https://osv.dev/vulnerability/CVE-2017-14608
Type: osv

## Details
In LibRaw through 0.18.4, an out of bounds read flaw related to kodak_65000_load_raw has been reported in dcraw/dcraw.c and internal/dcraw_common.cpp. An attacker could possibly exploit this flaw to disclose potentially sensitive memory or cause an application crash.

## References
- https://github.com/LibRaw/LibRaw/issues/101
- https://github.com/LibRaw/LibRaw/commit/d13e8f6d1e987b7491182040a188c16a395f1d21
