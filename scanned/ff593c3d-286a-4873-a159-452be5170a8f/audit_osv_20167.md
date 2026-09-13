# [M] CVE-2021-31821

## Summary
Severity: Medium
Advisory: CVE-2021-31821
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-01-19
Source: https://osv.dev/vulnerability/CVE-2021-31821
Type: osv

## Details
When the Windows Tentacle docker image starts up it logs all the commands that it runs along with the arguments, which writes the Octopus Server API key in plaintext. This does not affect the Linux Docker image

## References
- https://advisories.octopus.com/post/2022/sa2022-01/
