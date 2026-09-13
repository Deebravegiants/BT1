# [C] Cacti RCE vulnerability when importing packages

## Summary
Severity: Critical
Advisory: CVE-2024-25641
Aliases: GHSA-7cmj-g5qc-pj88
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-25641
Type: osv

## Details
Cacti provides an operational monitoring and fault management framework. Prior to version 1.2.27, an arbitrary file write vulnerability, exploitable through the "Package Import" feature, allows authenticated users having the "Import Templates" permission to execute arbitrary PHP code on the web server. The vulnerability is located within the `import_package()` function defined into the `/lib/import.php` script. The function blindly trusts the filename and file content provided within the XML data, and writes such files into the Cacti base path (or even outside, since path traversal sequences are not filtered). This can be exploited to write or overwrite arbitrary files on the web server, leading to execution of arbitrary PHP code or other security impacts. Version 1.2.27 contains a patch for this issue.

## References
- http://seclists.org/fulldisclosure/2024/May/6
- https://lists.debian.org/debian-lts-announce/2024/09/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RBEOAFKRARQHTDIYSL723XAFJ2Q6624X/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25641.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-7cmj-g5qc-pj88
- https://nvd.nist.gov/vuln/detail/CVE-2024-25641
- https://github.com/Cacti/cacti/commit/eff35b0ff26cc27c82d7880469ed6d5e3bef6210
