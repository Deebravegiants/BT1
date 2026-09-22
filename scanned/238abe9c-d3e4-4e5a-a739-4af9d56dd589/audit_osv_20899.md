# [H] CVE-2021-38185

## Summary
Severity: High
Advisory: CVE-2021-38185
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-08
Source: https://osv.dev/vulnerability/CVE-2021-38185
Type: osv

## Details
GNU cpio through 2.13 allows attackers to execute arbitrary code via a crafted pattern file, because of a dstring.c ds_fgetstr integer overflow that triggers an out-of-bounds heap write. NOTE: it is unclear whether there are common cases where the pattern file, associated with the -E option, is untrusted data.

## References
- https://lists.debian.org/debian-lts-announce/2023/06/msg00007.html
- https://git.savannah.gnu.org/cgit/cpio.git/commit/?id=dd96882877721703e19272fe25034560b794061b
- https://github.com/fangqyi/cpiopwn
- https://lists.gnu.org/archive/html/bug-cpio/2021-08/msg00000.html
- https://lists.gnu.org/archive/html/bug-cpio/2021-08/msg00002.html
