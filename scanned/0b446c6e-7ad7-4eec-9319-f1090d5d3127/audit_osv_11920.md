# [H] CVE-2018-1000098

## Summary
Severity: High
Advisory: CVE-2018-1000098
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-1000098
Type: osv

## Details
Teluu PJSIP version 2.7.1 and earlier contains a Integer Overflow vulnerability in pjmedia SDP parsing that can result in Crash. This attack appear to be exploitable via Sending a specially crafted message. This vulnerability appears to have been fixed in 2.7.2.

## References
- https://trac.pjsip.org/repos/milestone/release-2.7.2
- https://trac.pjsip.org/repos/ticket/2093
- https://www.debian.org/security/2018/dsa-4170
