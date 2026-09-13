# [C] CVE-2017-1000044

## Summary
Severity: Critical
Advisory: CVE-2017-1000044
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-1000044
Type: osv

## Details
gtk-vnc 0.4.2 and older doesn't check framebuffer boundaries correctly when updating framebuffer which may lead to memory corruption when rendering

## References
- https://git.gnome.org/browse/gtk-vnc/commit/?id=f3fc5e57a78d4be9872f1394f697b9929873a737
