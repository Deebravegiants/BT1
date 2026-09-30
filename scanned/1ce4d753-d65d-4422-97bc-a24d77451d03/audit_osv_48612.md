# [M] CVE-2018-1000532

## Summary
Severity: Medium
Advisory: CVE-2018-1000532
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000532
Type: osv

## Details
beep version 1.3 and up contains a External Control of File Name or Path vulnerability in --device option that can result in Local unprivileged user can inhibit execution of arbitrary programs by other users, allowing DoS. This attack appear to be exploitable via The system must allow local users to run beep.

## References
- https://github.com/johnath/beep/issues/11#issuecomment-379514298
