# [M] CVE-2022-0563

## Summary
Severity: Medium
Advisory: CVE-2022-0563
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-21
Source: https://osv.dev/vulnerability/CVE-2022-0563
Type: osv

## Details
A flaw was found in the util-linux chfn and chsh utilities when compiled with Readline support. The Readline library uses an "INPUTRC" environment variable to get a path to the library config file. When the library cannot parse the specified file, it prints an error message containing data from the file. This flaw allows an unprivileged user to read root-owned files, potentially leading to privilege escalation. This flaw affects util-linux versions prior to 2.37.4.

## References
- https://lore.kernel.org/util-linux/20220214110609.msiwlm457ngoic6w%40ws.net.home/T/#u
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0563.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-0563
- https://security.gentoo.org/glsa/202401-08
- https://security.netapp.com/advisory/ntap-20220331-0002/
