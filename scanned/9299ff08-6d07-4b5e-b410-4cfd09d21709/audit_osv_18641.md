# [H] CVE-2020-29394

## Summary
Severity: High
Advisory: CVE-2020-29394
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-11-30
Source: https://osv.dev/vulnerability/CVE-2020-29394
Type: osv

## Details
A buffer overflow in the dlt_filter_load function in dlt_common.c from dlt-daemon through 2.18.5 (GENIVI Diagnostic Log and Trace) allows arbitrary code execution because fscanf is misused (no limit on the number of characters to be read in the format argument).

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00016.html
- https://github.com/GENIVI/dlt-daemon/issues/274
- https://github.com/GENIVI/dlt-daemon/pull/275
- https://github.com/GENIVI/dlt-daemon/pull/288
