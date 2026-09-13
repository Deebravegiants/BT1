# [M] CVE-2018-1000161

## Summary
Severity: Medium
Advisory: CVE-2018-1000161
CVSS: 5.7 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-04-18
Source: https://osv.dev/vulnerability/CVE-2018-1000161
Type: osv

## Details
nmap version 6.49BETA6 through 7.60, up to and including SVN revision 37147 contains a Directory Traversal vulnerability in NSE script http-fetch that can result in file overwrite as the user is running it. This attack appears to be exploitable via a victim that runs NSE script http-fetch against a malicious web site. This vulnerability appears to have been fixed in 7.7.

## References
- https://nmap.org/changelog.html
