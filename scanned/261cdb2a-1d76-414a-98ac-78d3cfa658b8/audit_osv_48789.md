# [C] CVE-2018-13410

## Summary
Severity: Critical
Advisory: CVE-2018-13410
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-06
Source: https://osv.dev/vulnerability/CVE-2018-13410
Type: osv

## Details
Info-ZIP Zip 3.0, when the -T and -TT command-line options are used, allows attackers to cause a denial of service (invalid free and application crash) or possibly have unspecified other impact because of an off-by-one error. NOTE: it is unclear whether there are realistic scenarios in which an untrusted party controls the -TT value, given that the entire purpose of -TT is execution of arbitrary commands

## References
- http://seclists.org/fulldisclosure/2018/Jul/24
