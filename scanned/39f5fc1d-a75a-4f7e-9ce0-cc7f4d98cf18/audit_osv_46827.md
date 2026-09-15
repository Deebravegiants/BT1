# [H] CVE-2015-5236

## Summary
Severity: High
Advisory: CVE-2015-5236
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-07-07
Source: https://osv.dev/vulnerability/CVE-2015-5236
Type: osv

## Details
It was discovered that the IcedTea-Web used codebase attribute of the <applet> tag on the HTML page that hosts Java applet in the Same Origin Policy (SOP) checks. As the specified codebase does not have to match the applet's actual origin, this allowed malicious site to bypass SOP via spoofed codebase value.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1256403
- https://bugzilla.redhat.com/show_bug.cgi?id=1256403
- https://bugzilla.redhat.com/show_bug.cgi?id=1256403
