# [H] CVE-2021-3725

## Summary
Severity: High
Advisory: CVE-2021-3725
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-11-30
Source: https://osv.dev/vulnerability/CVE-2021-3725
Type: osv

## Details
Vulnerability in dirhistory plugin Description: the widgets that go back and forward in the directory history, triggered by pressing Alt-Left and Alt-Right, use functions that unsafely execute eval on directory names. If you cd into a directory with a carefully-crafted name, then press Alt-Left, the system is subject to command injection. Impacted areas: - Functions pop_past and pop_future in dirhistory plugin.

## References
- https://github.com/ohmyzsh/ohmyzsh/commit/06fc5fb
