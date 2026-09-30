# [M] ALPINE-CVE-2021-22922

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-22922
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22922
Type: osv

## Affected
- Alpine:v3.12: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.13: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.14: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.15: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.16: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.17: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.18: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.19: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.20: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.21: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.22: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.23: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.24: `curl` — affected >=7.27.0 <7.78.0-r0

## Details
When curl is instructed to download content using the metalink feature, thecontents is verified against a hash provided in the metalink XML file.The metalink XML file points out to the client how to get the same contentfrom a set of different URLs, potentially hosted by different servers and theclient can then download the file from one or several of them. In a serial orparallel manner.If one of the servers hosting the contents has been breached and the contentsof the specific file on that server is replaced with a modified payload, curlshould detect this when the hash of the file mismatches after a completeddownload. It should remove the contents and instead try getting the contentsfrom another URL. This is not done, and instead such a hash mismatch is onlymentioned in text and the potentially malicious content is kept in the file ondisk.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22922
