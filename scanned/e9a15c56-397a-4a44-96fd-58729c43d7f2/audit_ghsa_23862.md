# [H] Race Condition in Grunt

## Summary
Severity: High
Advisory: GHSA-rm36-94g8-835r
CVE: CVE-2022-1537
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-11
Source: https://github.com/advisories/GHSA-rm36-94g8-835r
Type: github-advisory

## Affected
- npm: `grunt` — affected >=0 <1.5.3

## Details
file.copy operations in GruntJS are vulnerable to a TOCTOU race condition leading to arbitrary file write in GitHub repository gruntjs/grunt prior to 1.5.3. This vulnerability is capable of arbitrary file writes which can lead to local privilege escalation to the GruntJS user if a lower-privileged user has write access to both source and destination directories as the lower-privileged user can create a symlink to the GruntJS user's .bashrc file or replace /etc/shadow file if the GruntJS user is root.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1537
- https://github.com/gruntjs/grunt/commit/58016ffac5ed9338b63ecc2a63710f5027362bae
- https://github.com/gruntjs/grunt
- https://huntr.dev/bounties/0179c3e5-bc02-4fc9-8491-a1a319b51b4d
- https://lists.debian.org/debian-lts-announce/2023/04/msg00006.html
