# [M] CVE-2015-9019

## Summary
Severity: Medium
Advisory: CVE-2015-9019
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-04-05
Source: https://osv.dev/vulnerability/CVE-2015-9019
Type: osv

## Details
In libxslt 1.1.29 and earlier, the EXSLT math.random function was not initialized with a random seed during startup, which could cause usage of this function to produce predictable outputs.

## References
- https://bugzilla.gnome.org/show_bug.cgi?id=758400
- https://bugzilla.suse.com/show_bug.cgi?id=934119
- https://bugzilla.gnome.org/show_bug.cgi?id=758400
- https://bugzilla.suse.com/show_bug.cgi?id=934119
- https://bugzilla.gnome.org/show_bug.cgi?id=758400
- https://bugzilla.suse.com/show_bug.cgi?id=934119
