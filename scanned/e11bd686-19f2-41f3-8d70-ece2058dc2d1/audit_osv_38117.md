# [H] HDF5: H5T__conv_struct Use After Free

## Summary
Severity: High
Advisory: CVE-2026-34734
Aliases: GHSA-w7v2-9cmr-pwwj
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-34734
Type: osv

## Details
HDF5 is software for managing data. In 1.14.1-2 and earlier, a heap-use-after-free was found in the h5dump helper utility. An attacker who can supply a malicious h5 file can trigger a heap use-after-free. The freed object is referenced in a memmove call from H5T__conv_struct. The original object was allocated by H5D__typeinfo_init_phase3 and freed by H5D__typeinfo_term.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34734.json
- https://access.redhat.com/security/cve/CVE-2026-34734
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34734.json
- https://github.com/HDFGroup/hdf5/security/advisories/GHSA-w7v2-9cmr-pwwj
- https://nvd.nist.gov/vuln/detail/CVE-2026-34734
- https://bugzilla.redhat.com/show_bug.cgi?id=2457034
