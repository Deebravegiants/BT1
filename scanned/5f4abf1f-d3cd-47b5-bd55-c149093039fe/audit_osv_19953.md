# [C] CVE-2021-28300

## Summary
Severity: Critical
Advisory: CVE-2021-28300
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2021-28300
Type: osv

## Details
NULL Pointer Dereference in the "isomedia/track.c" module's "MergeTrack()" function of GPAC v0.5.2 allows attackers to execute arbitrary code or cause a Denial-of-Service (DoS) by uploading a malicious MP4 file.

## References
- https://github.com/gpac/gpac/issues/1702
