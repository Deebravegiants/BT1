# [H] Gimp: stack-based buffer overflows in file-ico

## Summary
Severity: High
Advisory: CVE-2025-48796
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-48796
Type: osv

## Details
A flaw was found in GIMP. The GIMP ani_load_image() function is vulnerable to a stack-based overflow. If a user opens.ANI files, GIMP may be used to store more information than the capacity allows. This flaw allows a malicious ANI file to trigger arbitrary code execution.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://www.gimp.org/
- https://access.redhat.com/security/cve/CVE-2025-48796
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48796.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-48796
- https://bugzilla.redhat.com/show_bug.cgi?id=2368559
- https://gitlab.gnome.org/GNOME/gimp/-/issues/9257
