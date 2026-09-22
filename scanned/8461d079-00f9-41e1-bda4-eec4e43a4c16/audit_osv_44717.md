# [H] CVE-2026-85649

## Summary
Severity: High
Advisory: CVE-2026-85649
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85649
Type: osv

## Details
(Holloway) Chew, Kean Ho's Actualizer v1.2.0 and earlier contains a fail-open password validation vulnerability in the Alpha user and root user password loops of Shell/debian-minbase-install.sh. The installer invokes mkpasswd to generate yescrypt password hashes but does not check the command's return value and unconditionally accepts the result. If mkpasswd fails to generate a yescrypt hash, for example because an incompatible mkpasswd implementation or an environment without yescrypt support is used, the resulting password hash variable can be empty and the build proceeds. The resulting image can therefore contain empty password fields for the root and alpha accounts, potentially permitting passwordless authentication depending on the authentication configuration.

## References
- https://github.com/ChewKeanHo/software-actualizer/blob/v1.2.0/Shell/debian-minbase-install.sh#L788
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85649.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85649
- https://github.com/ChewKeanHo/software-actualizer/commit/50a0932ac705635d9af62955c353e7c6df003a61.patch
- https://github.com/ChewKeanHo/software-actualizer/releases/tag/v1.2.1
- https://doi.org/10.5281/zenodo.22169659
