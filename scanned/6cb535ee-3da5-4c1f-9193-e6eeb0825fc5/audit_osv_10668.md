# [H] CVE-2017-18120

## Summary
Severity: High
Advisory: CVE-2017-18120
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2017-18120
Type: osv

## Details
A double-free bug in the read_gif function in gifread.c in gifsicle 1.90 allows a remote attacker to cause a denial-of-service attack or unspecified other impact via a maliciously crafted file, because last_name is mishandled, a different vulnerability than CVE-2017-1000421.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=878739
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=881120
- https://github.com/kohler/gifsicle/issues/117
- https://github.com/kohler/gifsicle/commit/118a46090c50829dc543179019e6140e1235f909
