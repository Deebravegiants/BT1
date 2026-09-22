# [H] CVE-2020-5291

## Summary
Severity: High
Advisory: CVE-2020-5291
Aliases: GHSA-j2qp-rvxj-43vj
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-31
Source: https://osv.dev/vulnerability/CVE-2020-5291
Type: osv

## Details
Bubblewrap (bwrap) before version 0.4.1, if installed in setuid mode and the kernel supports unprivileged user namespaces, then the `bwrap --userns2` option can be used to make the setuid process keep running as root while being traceable. This can in turn be used to gain root permissions. Note that this only affects the combination of bubblewrap in setuid mode (which is typically used when unprivileged user namespaces are not supported) and the support of unprivileged user namespaces. Known to be affected are: * Debian testing/unstable, if unprivileged user namespaces enabled (not default) * Debian buster-backports, if unprivileged user namespaces enabled (not default) * Arch if using `linux-hardened`, if unprivileged user namespaces enabled (not default) * Centos 7 flatpak COPR, if unprivileged user namespaces enabled (not default) This has been fixed in the 0.4.1 release, and all affected users should update.

## References
- https://github.com/containers/bubblewrap/security/advisories/GHSA-j2qp-rvxj-43vj
- https://github.com/containers/bubblewrap/commit/1f7e2ad948c051054b683461885a0215f1806240
