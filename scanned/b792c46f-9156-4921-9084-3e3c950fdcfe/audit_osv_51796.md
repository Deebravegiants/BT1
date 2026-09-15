# [M] CVE-2021-40648

## Summary
Severity: Medium
Advisory: CVE-2021-40648
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-09
Source: https://osv.dev/vulnerability/CVE-2021-40648
Type: osv

## Details
In man2html 1.6g, a filename can be created to overwrite the previous size parameter of the next chunk and the fd, bk, fd_nextsize, bk_nextsize of the current chunk. The next chunk is then freed later on, causing a freeing of an arbitrary amount of memory.

## References
- https://gist.github.com/untaman/cb58123fe89fc65e3984165db5d40933
