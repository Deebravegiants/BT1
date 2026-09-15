# [H] CVE-2020-13847

## Summary
Severity: High
Advisory: CVE-2020-13847
Aliases: GHSA-m7j2-9565-4h9v
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-07-14
Source: https://osv.dev/vulnerability/CVE-2020-13847
Type: osv

## Details
Sylabs Singularity 3.0 through 3.5 lacks support for an Integrity Check. Singularity's sign and verify commands do not sign metadata found in the global header or data object descriptors of a SIF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00053.html
- https://github.com/hpcng/singularity/security/advisories/GHSA-m7j2-9565-4h9v
- https://medium.com/sylabs
