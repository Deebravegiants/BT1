# [H] CVE-2018-1000097

## Summary
Severity: High
Advisory: CVE-2018-1000097
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-1000097
Type: osv

## Details
Sharutils sharutils (unshar command) version 4.15.2 contains a Buffer Overflow vulnerability in Affected component on the file unshar.c at line 75, function looks_like_c_code. Failure to perform checking of the buffer containing input line. that can result in Could lead to code execution. This attack appear to be exploitable via Victim have to run unshar command on a specially crafted file..

## References
- http://seclists.org/bugtraq/2018/Feb/54
- https://usn.ubuntu.com/3605-1/
- https://www.debian.org/security/2018/dsa-4167
