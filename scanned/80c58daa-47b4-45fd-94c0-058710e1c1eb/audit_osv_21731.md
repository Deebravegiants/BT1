# [M] CVE-2021-46019

## Summary
Severity: Medium
Advisory: CVE-2021-46019
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2021-46019
Type: osv

## Details
An untrusted pointer dereference in rec_db_destroy() at rec-db.c of GNU Recutils v1.8.90 can lead to a segmentation fault or application crash.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TDVOFC3HTBG7DF2PZTEXRMG4CV2F55UF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VRSXSN2XF6PX74WDYVV26TQMYIFAEQ3T/
- https://github.com/gnu-mirror-unofficial/recutils/commit/34b75ed7ad492c8e38b669ebafe0176f1f9992d2
- https://lists.gnu.org/archive/html/bug-recutils/2021-12/msg00009.html
