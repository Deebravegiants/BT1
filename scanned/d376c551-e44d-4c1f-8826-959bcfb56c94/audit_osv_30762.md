# [C] Malicious plugin names, recipients, or identities can cause arbitrary binary execution in pyrage

## Summary
Severity: Critical
Advisory: CVE-2024-56327
Aliases: GHSA-47h8-jmp3-9f28, PYSEC-2026-1839
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-19
Source: https://osv.dev/vulnerability/CVE-2024-56327
Type: osv

## Details
pyrage is a set of Python bindings for the rage file encryption library (age in Rust). `pyrage` uses the Rust `age` crate for its underlying operations, and `age` is vulnerable to GHSA-4fg7-vxc8-qx5w. All details of GHSA-4fg7-vxc8-qx5w are relevant to `pyrage` for the versions specified in this advisory. See GHSA-4fg7-vxc8-qx5w for full details. Versions of `pyrage` before 1.2.0 lack plugin support and are therefore **not affected**. An equivalent issue was fixed in [the reference Go implementation of age](https://github.com/FiloSottile/age), see advisory GHSA-32gq-x56h-299c. This issue has been addressed in version 1.2.3 and all users are advised to update. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56327.json
- https://github.com/FiloSottile/age/security/advisories/GHSA-32gq-x56h-299c
- https://github.com/advisories/GHSA-4fg7-vxc8-qx5w
- https://github.com/woodruffw/pyrage/security/advisories/GHSA-47h8-jmp3-9f28
- https://nvd.nist.gov/vuln/detail/CVE-2024-56327
