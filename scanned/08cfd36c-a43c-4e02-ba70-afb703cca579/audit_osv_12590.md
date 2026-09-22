# [H] CVE-2018-13066

## Summary
Severity: High
Advisory: CVE-2018-13066
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-02
Source: https://osv.dev/vulnerability/CVE-2018-13066
Type: osv

## Details
There is a memory leak in util/parser.c in libming 0.4.8, which will lead to a denial of service via parseSWF_DEFINEBUTTON2, parseSWF_DEFINEFONT, parseSWF_DEFINEFONTINFO, parseSWF_DEFINELOSSLESS, parseSWF_DEFINESPRITE, parseSWF_DEFINETEXT, parseSWF_DOACTION, parseSWF_FILLSTYLEARRAY, parseSWF_FRAMELABEL, parseSWF_LINESTYLEARRAY, parseSWF_PLACEOBJECT2, or parseSWF_SHAPEWITHSTYLE.

## References
- https://github.com/libming/libming/issues/146
