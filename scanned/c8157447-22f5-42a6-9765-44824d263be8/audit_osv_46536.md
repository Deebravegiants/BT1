# [H] CVE-2012-6711

## Summary
Severity: High
Advisory: CVE-2012-6711
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-18
Source: https://osv.dev/vulnerability/CVE-2012-6711
Type: osv

## Details
A heap-based buffer overflow exists in GNU Bash before 4.3 when wide characters, not supported by the current locale set in the LC_CTYPE environment variable, are printed through the echo built-in function. A local attacker, who can provide data to print through the "echo -e" built-in function, may use this flaw to crash a script or execute code with the privileges of the bash process. This occurs because ansicstr() in lib/sh/strtrans.c mishandles u32cconv().

## References
- http://git.savannah.gnu.org/cgit/bash.git/commit/?h=devel&id=863d31ae775d56b785dc5b0105b6d251515d81d5
- https://bugzilla.redhat.com/show_bug.cgi?id=1721071
- http://git.savannah.gnu.org/cgit/bash.git/commit/?h=devel&id=863d31ae775d56b785dc5b0105b6d251515d81d5
- http://git.savannah.gnu.org/cgit/bash.git/commit/?h=devel&id=863d31ae775d56b785dc5b0105b6d251515d81d5
- https://bugzilla.redhat.com/show_bug.cgi?id=1721071
- http://www.securityfocus.com/bid/108824
- https://support.f5.com/csp/article/K05122252
- https://support.f5.com/csp/article/K05122252?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4180-1/
