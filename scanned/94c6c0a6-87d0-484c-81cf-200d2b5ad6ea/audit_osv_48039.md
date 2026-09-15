# [H] CVE-2017-17513

## Summary
Severity: High
Advisory: CVE-2017-17513
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-14
Source: https://osv.dev/vulnerability/CVE-2017-17513
Type: osv

## Details
TeX Live through 20170524 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL, related to linked_scripts/context/stubs/unix/mtxrun, texmf-dist/scripts/context/stubs/mswin/mtxrun.lua, and texmf-dist/tex/luatex/lualibs/lualibs-os.lua.

## References
- https://security-tracker.debian.org/tracker/CVE-2017-17513
