# [H] ALPINE-CVE-2021-28677

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28677
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28677
Type: osv

## Affected
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.2.0-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.2.0-r0

## Details
An issue was discovered in Pillow before 8.2.0. For EPS data, the readline implementation used in EPSImageFile has to deal with any combination of \r and \n as line endings. It used an accidentally quadratic method of accumulating lines while looking for a line ending. A malicious EPS file could use this to perform a DoS of Pillow in the open phase, before an image was accepted for opening.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28677
