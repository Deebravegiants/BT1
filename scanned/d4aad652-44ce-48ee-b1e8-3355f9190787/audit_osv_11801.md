# [H] CVE-2017-9780

## Summary
Severity: High
Advisory: CVE-2017-9780
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-21
Source: https://osv.dev/vulnerability/CVE-2017-9780
Type: osv

## Details
In Flatpak before 0.8.7, a third-party app repository could include malicious apps that contain files with inappropriate permissions, for example setuid or world-writable. The files are deployed with those permissions, which would let a local attacker run the setuid executable or write to the world-writable location. In the case of the "system helper" component, files deployed as part of the app are owned by root, so in the worst case they could be setuid root.

## References
- http://www.debian.org/security/2017/dsa-3895
- http://www.securityfocus.com/bid/99346
- https://bugs.debian.org/865413
- https://github.com/flatpak/flatpak/issues/845
