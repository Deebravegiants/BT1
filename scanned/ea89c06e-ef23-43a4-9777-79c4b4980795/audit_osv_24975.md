# [H] Git for Windows's config file of `connect.exe` is susceptible to malicious placing

## Summary
Severity: High
Advisory: CVE-2023-29011
Aliases: GHSA-g4fv-xjqw-q7jm
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-04-25
Source: https://osv.dev/vulnerability/CVE-2023-29011
Type: osv

## Details
Git for Windows, the Windows port of Git, ships with an executable called `connect.exe`, which implements a SOCKS5 proxy that can be used to connect e.g. to SSH servers via proxies when certain ports are blocked for outgoing connections. The location of `connect.exe`'s config file is hard-coded as `/etc/connectrc` which will typically be interpreted as `C:\etc\connectrc`. Since `C:\etc` can be created by any authenticated user, this makes `connect.exe` susceptible to malicious files being placed there by other users on the same multi-user machine. The problem has been patched in Git for Windows v2.40.1. As a workaround, create the folder `etc` on all drives where Git commands are run, and remove read/write access from those folders. Alternatively, watch out for malicious `<drive>:\etc\connectrc` files on multi-user machines.

## References
- https://github.com/git-for-windows/git/releases/tag/v2.40.1.windows.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29011.json
- https://github.com/git-for-windows/git/security/advisories/GHSA-g4fv-xjqw-q7jm
- https://nvd.nist.gov/vuln/detail/CVE-2023-29011
