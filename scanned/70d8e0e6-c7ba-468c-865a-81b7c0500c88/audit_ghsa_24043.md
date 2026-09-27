# [M] Default inheritable capabilities for linux container should be empty

## Summary
Severity: Medium
Advisory: GHSA-f3fp-gc8g-vw66
CVE: CVE-2022-29162
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f3fp-gc8g-vw66
Type: github-advisory

## Affected
- Go: `github.com/opencontainers/runc` — affected >=0 <1.1.2

## Details
### Impact

A bug was found in runc where `runc exec --cap` executed processes with non-empty inheritable Linux process capabilities, creating an atypical Linux environment and enabling programs with inheritable file capabilities to elevate those capabilities to the permitted set during execve(2).

This bug did not affect the container security sandbox as the inheritable set never contained more capabilities than were included in the container's bounding set.

### Patches
This bug has been fixed in runc 1.1.2. Users should update to this version as soon as possible.

This fix changes `runc exec --cap` behavior such that the additional capabilities granted to the process being executed (as specified via `--cap` arguments) do not include inheritable capabilities.

In addition, `runc spec` is changed to not set any inheritable capabilities in the created example OCI spec (`config.json`) file.

### Credits
The opencontainers project would like to thank [Andrew G. Morgan](https://github.com/AndrewGMorgan) for responsibly disclosing this issue in accordance with the [opencontainers org security policy](https://github.com/opencontainers/.github/blob/master/SECURITY.md).

### For more information
If you have any questions or comments about this advisory:

* [Open an issue](https://github.com/opencontainers/runc/issues/new)
* Email us at [security@opencontainers.org](mailto:security@opencontainers.org) if you think you’ve found a security bug

## References
- https://github.com/opencontainers/runc/security/advisories/GHSA-f3fp-gc8g-vw66
- https://nvd.nist.gov/vuln/detail/CVE-2022-29162
- https://github.com/opencontainers/runc/commit/d04de3a9b72d7a2455c1885fc75eb36d02cd17b5
- https://github.com/opencontainers/runc/releases/tag/v1.1.2
- https://lists.debian.org/debian-lts-announce/2023/03/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AVPZBV7ISA7QKRPTC7ZXWKMIQI2HZEBB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D77CKD3AXPMU4PMQIQI5Q74SI4JATNND
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GPQU4YC4AAY54JDXGDQHJEYKSXXG5T2Y
- github.com/opencontainers/runc
