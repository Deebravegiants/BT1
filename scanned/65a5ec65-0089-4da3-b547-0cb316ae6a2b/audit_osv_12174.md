# [M] CVE-2018-10767

## Summary
Severity: Medium
Advisory: CVE-2018-10767
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-06
Source: https://osv.dev/vulnerability/CVE-2018-10767
Type: osv

## Details
There is a stack-based buffer over-read in calling GLib in the function gxps_images_guess_content_type of gxps-images.c in libgxps through 0.3.0 because it does not reject negative return values from a g_input_stream_read call. A crafted input will lead to a remote denial of service attack.

## References
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3140
- https://access.redhat.com/errata/RHSA-2018:3505
- https://bugzilla.redhat.com/show_bug.cgi?id=1575188
