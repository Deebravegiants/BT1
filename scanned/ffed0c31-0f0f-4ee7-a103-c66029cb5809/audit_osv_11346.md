# [H] CVE-2017-7500

## Summary
Severity: High
Advisory: CVE-2017-7500
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-13
Source: https://osv.dev/vulnerability/CVE-2017-7500
Type: osv

## Details
It was found that rpm did not properly handle RPM installations when a destination path was a symbolic link to a directory, possibly changing ownership and permissions of an arbitrary directory, and RPM files being placed in an arbitrary destination. An attacker, with write access to a directory in which a subdirectory will be installed, could redirect that directory to an arbitrary location and gain root privilege.

## References
- https://github.com/rpm-software-management/rpm/commit/c815822c8bdb138066ff58c624ae83e3a12ebfa9
- https://github.com/rpm-software-management/rpm/commit/f2d3be2a8741234faaa96f5fd05fdfdc75779a79
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7500
