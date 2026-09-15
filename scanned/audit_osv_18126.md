# [H] CVE-2020-24307

## Summary
Severity: High
Advisory: CVE-2020-24307
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-02
Source: https://osv.dev/vulnerability/CVE-2020-24307
Type: osv

## Details
An issue in mRemoteNG v1.76.20 allows attackers to escalate privileges via a crafted executable file. NOTE: third parties were unable to reproduce any scenario in which the claimed access of BUILTIN\Users:(M) is present.

## References
- https://github.com/NyaMeeEain/Infrastructure-Assessment/blob/master/Privilege%20Escalation/Common%20Windows%20Privilege%20Escalation.md
- https://packetstormsecurity.com/files/170794/mRemoteNG-1.76.20-Privilege-Escalation.html
- https://github.com/mRemoteNG/mRemoteNG/issues/2338
