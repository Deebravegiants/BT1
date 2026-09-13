# [M] CVE-2020-29385

## Summary
Severity: Medium
Advisory: CVE-2020-29385
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-26
Source: https://osv.dev/vulnerability/CVE-2020-29385
Type: osv

## Details
GNOME gdk-pixbuf (aka GdkPixbuf) before 2.42.2 allows a denial of service (infinite loop) in lzw.c in the function write_indexes. if c->self_code equals 10, self->code_table[10].extends will assign the value 11 to c. The next execution in the loop will assign self->code_table[11].extends to c, which will give the value of 10. This will make the loop run infinitely. This bug can, for example, be triggered by calling this function with a GIF image with LZW compression that is crafted in a special way.

## References
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/blob/master/NEWS
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/issues/164
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B5H3GNVWMZTYZR3JBYCK57PF7PFMQBNP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BGZVCTH5O7WBJLYXZ2UOKLYNIFPVR55D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EANWYODLOJDFLMBH6WEKJJMQ5PKLEWML/
- https://security.gentoo.org/glsa/202012-15
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=977166
- https://ubuntu.com/security/CVE-2020-29385
