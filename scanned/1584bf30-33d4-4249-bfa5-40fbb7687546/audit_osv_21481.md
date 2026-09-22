# [H] CVE-2021-43396

## Summary
Severity: High
Advisory: CVE-2021-43396
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-11-04
Source: https://osv.dev/vulnerability/CVE-2021-43396
Type: osv

## Details
In iconvdata/iso-2022-jp-3.c in the GNU C Library (aka glibc) 2.34, remote attackers can force iconv() to emit a spurious '\0' character via crafted ISO-2022-JP-3 data that is accompanied by an internal state reset. This may affect data integrity in certain iconv() use cases. NOTE: the vendor states "the bug cannot be invoked through user input and requires iconv to be invoked with a NULL inbuf, which ought to require a separate application bug to do so unintentionally. Hence there's no security impact to the bug.

## References
- https://sourceware.org/git/?p=glibc.git%3Ba=commit%3Bh=ff012870b2c02a62598c04daa1e54632e020fd7d
- https://sourceware.org/bugzilla/show_bug.cgi?id=28524
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://blog.tuxcare.com/vulnerability/vulnerability-in-iconv-identified-by-tuxcare-team-cve-2021-43396
