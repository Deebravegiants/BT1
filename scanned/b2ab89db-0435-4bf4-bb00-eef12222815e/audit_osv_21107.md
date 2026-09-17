# [M] CVE-2021-40592

## Summary
Severity: Medium
Advisory: CVE-2021-40592
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-06-08
Source: https://osv.dev/vulnerability/CVE-2021-40592
Type: osv

## Details
GPAC version before commit 71460d72ec07df766dab0a4d52687529f3efcf0a (version v1.0.1 onwards) contains loop with unreachable exit condition ('infinite loop') vulnerability in ISOBMFF reader filter, isoffin_read.c. Function isoffin_process() can result in DoS by infinite loop. To exploit, the victim must open a specially crafted mp4 file.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1876
- https://github.com/gpac/gpac/commit/71460d72ec07df766dab0a4d52687529f3efcf0a
