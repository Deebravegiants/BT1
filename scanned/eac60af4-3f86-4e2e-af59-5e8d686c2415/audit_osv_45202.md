# [M] A flaw was found in the util-linux chfn and chsh utilities when compiled with Readline support

## Summary
Severity: Medium
Advisory: JLSEC-2025-191
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/JLSEC-2025-191
Type: osv

## Affected
- Julia: `Libmount_jll` — affected >=0 <2.39.3+0
- Julia: `Libuuid_jll` — affected >=0 <2.39.3+0
- Julia: `util_linux_jll` — affected >=0 <2.39.3+0

## Details
A flaw was found in the util-linux chfn and chsh utilities when compiled with Readline support. The Readline library uses an "INPUTRC" environment variable to get a path to the library config file. When the library cannot parse the specified file, it prints an error message containing data from the file. This flaw allows an unprivileged user to read root-owned files, potentially leading to privilege escalation. This flaw affects util-linux versions prior to 2.37.4.

## References
- https://lore.kernel.org/util-linux/20220214110609.msiwlm457ngoic6w%40ws.net.home/T/#u
- https://security.gentoo.org/glsa/202401-08
- https://security.netapp.com/advisory/ntap-20220331-0002/
