# [M] CVE-2017-14604

## Summary
Severity: Medium
Advisory: CVE-2017-14604
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-09-20
Source: https://osv.dev/vulnerability/CVE-2017-14604
Type: osv

## Details
GNOME Nautilus before 3.23.90 allows attackers to spoof a file type by using the .desktop file extension, as demonstrated by an attack in which a .desktop file's Name field ends in .pdf but this file's Exec field launches a malicious "sh -c" command. In other words, Nautilus provides no UI indication that a file actually has the potentially unsafe .desktop extension; instead, the UI only shows the .pdf extension. One (slightly) mitigating factor is that an attack requires the .desktop file to have execute permission. The solution is to ask the user to confirm that the file is supposed to be treated as a .desktop file, and then remember the user's answer in the metadata::trusted field.

## References
- http://www.debian.org/security/2017/dsa-3994
- http://www.securityfocus.com/bid/101012
- https://access.redhat.com/errata/RHSA-2018:0223
- https://github.com/freedomofpress/securedrop/issues/2238
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=860268
- https://bugzilla.gnome.org/show_bug.cgi?id=777991
- https://github.com/GNOME/nautilus/commit/1630f53481f445ada0a455e9979236d31a8d3bb0
- https://github.com/GNOME/nautilus/commit/bc919205bf774f6af3fa7154506c46039af5a69b
- https://micahflee.com/2017/04/breaking-the-security-model-of-subgraph-os/
