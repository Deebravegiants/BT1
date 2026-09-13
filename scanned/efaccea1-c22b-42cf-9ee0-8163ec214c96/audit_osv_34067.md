# [M] AIDE improper output neutralization vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-54389
Aliases: GHSA-522j-vvx9-gg28
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-08-14
Source: https://osv.dev/vulnerability/CVE-2025-54389
Type: osv

## Details
AIDE is an advanced intrusion detection environment. Prior to version 0.19.2, there is an improper output neutralization vulnerability in AIDE.  An attacker can craft a malicious filename by including terminal escape sequences to hide the addition or removal of the file from the report and/or tamper with the log output. A local user might exploit this to bypass the AIDE detection of malicious files. Additionally the output of extended attribute key names and symbolic links targets are also not properly neutralized. This issue has been patched in version 0.19.2. A workaround involves configuring AIDE to write the report output to a regular file, redirecting stdout to a regular file, or redirecting the log output written to stderr to a regular file.

## References
- http://www.openwall.com/lists/oss-security/2025/08/14/7
- https://github.com/aide/aide/releases/tag/v0.19.2
- https://lists.debian.org/debian-lts-announce/2025/08/msg00011.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54389.json
- https://github.com/aide/aide/security/advisories/GHSA-522j-vvx9-gg28
- https://nvd.nist.gov/vuln/detail/CVE-2025-54389
- https://github.com/aide/aide/commit/64c8f32b0349c33fb8382784af468338078851f9
