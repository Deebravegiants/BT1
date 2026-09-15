# [H] CVE-2017-2908

## Summary
Severity: High
Advisory: CVE-2017-2908
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2017-2908
Type: osv

## Details
An exploitable integer overflow exists in the thumbnail functionality of the Blender open-source 3d creation suite version 2.78c. A specially crafted .blend file can cause an integer overflow resulting in a buffer overflow which can allow for code execution under the context of the application. An attacker can convince a user to render the thumbnail for the file while in the File->Open dialog.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00011.html
- https://www.debian.org/security/2018/dsa-4248
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0415
