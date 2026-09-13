# [M] CVE-2019-1010232

## Summary
Severity: Medium
Advisory: CVE-2019-1010232
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-22
Source: https://osv.dev/vulnerability/CVE-2019-1010232
Type: osv

## Details
Juniper juniper/libslax libslax latest version (as of commit 084ddf6ab4a55b59dfa9a53f9c5f14d192c4f8e5 Commits on Sep 1, 2018) is affected by: Buffer Overflow. The impact is: remote dos. The component is: slaxlexer.c:601(funtion:slaxGetInput). The attack vector is: ./slaxproc --slax-to-xslt POC0.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1649175
