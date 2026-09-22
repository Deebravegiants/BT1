# [M] CVE-2023-29581

## Summary
Severity: Medium
Advisory: CVE-2023-29581
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-12
Source: https://osv.dev/vulnerability/CVE-2023-29581
Type: osv

## Details
yasm 1.3.0.55.g101bc has a segmentation violation in the function delete_Token at modules/preprocs/nasm/nasm-pp.c. NOTE: although a libyasm application could become unavailable if this were exploited, the vendor's position is that there is no security relevance because there is either supposed to be input validation before data reaches libyasm, or a sandbox in which the application runs.

## References
- https://github.com/yasm/yasm/blob/master/SECURITY.md
- https://bugzilla.redhat.com/show_bug.cgi?id=2186333
- https://github.com/yasm/yasm/issues/216
- https://github.com/z1r00/fuzz_vuln/blob/main/yasm/segv/delete_Token/readme.md
