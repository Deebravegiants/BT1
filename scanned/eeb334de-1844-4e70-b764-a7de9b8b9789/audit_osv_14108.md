# [C] CVE-2018-7247

## Summary
Severity: Critical
Advisory: CVE-2018-7247
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-19
Source: https://osv.dev/vulnerability/CVE-2018-7247
Type: osv

## Details
An issue was discovered in pixHtmlViewer in prog/htmlviewer.c in Leptonica before 1.75.3. Unsanitized input (rootname) can overflow a buffer, leading potentially to arbitrary code execution or possibly unspecified other impact.

## References
- https://github.com/DanBloomberg/leptonica/commit/c1079bb8e77cdd426759e466729917ca37a3ed9f
- https://security.gentoo.org/glsa/202312-01
