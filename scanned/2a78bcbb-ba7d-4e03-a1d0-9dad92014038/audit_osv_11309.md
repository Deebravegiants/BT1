# [H] CVE-2017-7358

## Summary
Severity: High
Advisory: CVE-2017-7358
CVSS: 7.3 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-05
Source: https://osv.dev/vulnerability/CVE-2017-7358
Type: osv

## Details
In LightDM through 1.22.0, a directory traversal issue in debian/guest-account.sh allows local attackers to own arbitrary directory path locations and escalate privileges to root when the guest user logs out.

## References
- https://www.exploit-db.com/exploits/41923/
- http://bazaar.launchpad.net/~lightdm-team/lightdm/trunk/revision/2478
- http://www.securityfocus.com/bid/97486
- https://launchpad.net/bugs/1677924
- https://lists.freedesktop.org/archives/lightdm/2017-April/001059.html
- https://www.ubuntu.com/usn/usn-3255-1/
