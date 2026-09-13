# [M] CVE-2017-16942

## Summary
Severity: Medium
Advisory: CVE-2017-16942
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-25
Source: https://osv.dev/vulnerability/CVE-2017-16942
Type: osv

## Details
In libsndfile 1.0.25 (fixed in 1.0.26), a divide-by-zero error exists in the function wav_w64_read_fmt_chunk() in wav_w64.c, which may lead to DoS when playing a crafted audio file.

## References
- https://usn.ubuntu.com/4013-1/
- https://github.com/erikd/libsndfile/issues/341
