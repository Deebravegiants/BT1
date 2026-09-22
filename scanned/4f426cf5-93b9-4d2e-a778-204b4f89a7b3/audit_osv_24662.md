# [H] Command injection in cups-filters

## Summary
Severity: High
Advisory: CVE-2023-24805
Aliases: GHSA-gpxc-v2m8-fr3x
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-17
Source: https://osv.dev/vulnerability/CVE-2023-24805
Type: osv

## Details
cups-filters contains backends, filters, and other software required to get the cups printing service working on operating systems other than macos. If you use the Backend Error Handler (beh) to create an accessible network printer, this security vulnerability can cause remote code execution. `beh.c` contains the line `retval = system(cmdline) >> 8;` which calls the `system` command with the operand `cmdline`. `cmdline` contains multiple user controlled, unsanitized values. As a result an attacker with network access to the hosted print server can exploit this vulnerability to inject system commands which are executed in the context of the running server. This issue has been addressed in commit `8f2740357` and is expected to be bundled in the next release. Users are advised to upgrade when possible and to restrict access to network printers in the meantime.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KL2SJMZQ5T5JIH3PMQ2CGCY5TUUE255Y/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YNCGL2ZTAS2GFF23QFT55UFWIDMI4ZJK/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24805.json
- https://github.com/OpenPrinting/cups-filters/security/advisories/GHSA-gpxc-v2m8-fr3x
- https://nvd.nist.gov/vuln/detail/CVE-2023-24805
- https://security.gentoo.org/glsa/202401-06
- https://www.debian.org/security/2023/dsa-5407
- https://github.com/OpenPrinting/cups-filters/commit/8f274035756c04efeb77eb654e9d4c4447287d65
