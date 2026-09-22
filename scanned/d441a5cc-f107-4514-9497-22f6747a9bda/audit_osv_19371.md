# [M] CVE-2021-20315

## Summary
Severity: Medium
Advisory: CVE-2021-20315
CVSS: 6.1 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2021-20315
Type: osv

## Details
A locking protection bypass flaw was found in some versions of gnome-shell as shipped within CentOS Stream 8, when the "Application menu" or "Window list" GNOME extensions are enabled. This flaw allows a physical attacker who has access to a locked system to kill existing applications and start new ones as the locked user, even if the session is still locked.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2006285
