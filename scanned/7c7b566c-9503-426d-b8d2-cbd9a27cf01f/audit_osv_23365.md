# [H] CVE-2022-48363

## Summary
Severity: High
Advisory: CVE-2022-48363
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-26
Source: https://osv.dev/vulnerability/CVE-2022-48363
Type: osv

## Details
In MPD before 0.23.8, as used on Automotive Grade Linux and other platforms, the PipeWire output plugin mishandles a Drain call in certain situations involving truncated files. Eventually there is an assertion failure in libmpdclient because libqtappfw passes in a NULL pointer.

## References
- https://gerrit.automotivelinux.org/gerrit/c/src/libqtappfw/+/28484
- https://gerrit.automotivelinux.org/gerrit/c/src/libqtappfw/+/28485
- https://gerrit.automotivelinux.org/gerrit/q/project:src%252Flibqtappfw+status:open
- https://jira.automotivelinux.org/browse/SPEC-4661
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48363.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48363
