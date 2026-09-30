# [H] CVE-2020-35736

## Summary
Severity: High
Advisory: CVE-2020-35736
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-27
Source: https://osv.dev/vulnerability/CVE-2020-35736
Type: osv

## Details
GateOne 1.1 allows arbitrary file download without authentication via /downloads/.. directory traversal because os.path.join is misused.

## References
- https://github.com/liftoff/GateOne/issues/747
- https://rmb122.com/2019/08/28/Ogeek-Easy-Realworld-Challenge-1-2-Writeup/
