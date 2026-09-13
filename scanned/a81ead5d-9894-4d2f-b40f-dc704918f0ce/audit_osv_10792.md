# [H] CVE-2017-2663

## Summary
Severity: High
Advisory: CVE-2017-2663
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2663
Type: osv

## Details
It was found that subscription-manager's DBus interface before 1.19.4 let unprivileged user access the com.redhat.RHSM1.Facts.GetFacts and com.redhat.RHSM1.Config.Set methods. An unprivileged local attacker could use these methods to gain access to private information, or launch a privilege escalation attack.

## References
- http://www.securityfocus.com/bid/97015
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2663
- https://github.com/candlepin/subscription-manager/commit/2aa48ef65
