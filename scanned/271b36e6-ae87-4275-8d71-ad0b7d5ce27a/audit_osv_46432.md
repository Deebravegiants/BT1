# [H] CVE-2010-3843

## Summary
Severity: High
Advisory: CVE-2010-3843
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2010-3843
Type: osv

## Details
The GTK version of ettercap uses a global settings file at /tmp/.ettercap_gtk and does not verify ownership of this file. When parsing this file for settings in gtkui_conf_read() (src/interfacesgtk/ec_gtk_conf.c), an unchecked sscanf() call allows a maliciously placed settings file to overflow a statically-sized buffer on the stack.

## References
- https://bugs.launchpad.net/ubuntu/+source/ettercap/+bug/656347
- https://bugzilla.redhat.com/show_bug.cgi?id=643453
- https://bugs.launchpad.net/ubuntu/+source/ettercap/+bug/656347
- https://bugzilla.redhat.com/show_bug.cgi?id=643453
- http://article.gmane.org/gmane.comp.security.oss.general/3660
