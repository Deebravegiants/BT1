# [H] CVE-2019-1789

## Summary
Severity: High
Advisory: CVE-2019-1789
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-05
Source: https://osv.dev/vulnerability/CVE-2019-1789
Type: osv

## Details
ClamAV versions prior to 0.101.2 are susceptible to a denial of service (DoS) vulnerability. An out-of-bounds heap read condition may occur when scanning PE files. An example is Windows EXE and DLL files that have been packed using Aspack as a result of inadequate bound-checking.

## References
- https://blog.clamav.net/2019/03/clamav-01012-and-01003-patches-have.html
