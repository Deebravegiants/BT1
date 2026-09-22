# [M] CVE-2021-29453

## Summary
Severity: Medium
Advisory: CVE-2021-29453
Aliases: GHSA-j889-h476-hh9h
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-29453
Type: osv

## Details
matrix-media-repo is an open-source multi-domain media repository for Matrix. Versions 1.2.6 and earlier of matrix-media-repo do not properly handle malicious images which are crafted to be small in file size, but large in complexity. A malicious user could upload a relatively small image in terms of file size, using particular image formats, which expands to have extremely large dimensions during the process of thumbnailing. The server can be exhausted of memory in the process of trying to load the whole image into memory for thumbnailing, leading to denial of service. Version 1.2.7 has a fix for the vulnerability.

## References
- https://github.com/turt2live/matrix-media-repo/releases/tag/v1.2.7
- https://hub.docker.com/r/turt2live/matrix-media-repo/tags?page=1&ordering=last_updated
- https://github.com/turt2live/matrix-media-repo/security/advisories/GHSA-j889-h476-hh9h
