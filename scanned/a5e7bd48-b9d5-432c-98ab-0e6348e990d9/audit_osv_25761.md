# [M] CVE-2023-43771

## Summary
Severity: Medium
Advisory: CVE-2023-43771
CVSS: 5.5 (CVSS:3.1/AC:L/AV:L/A:H/C:N/I:N/PR:L/S:U/UI:N)
Published: 2023-09-22
Source: https://osv.dev/vulnerability/CVE-2023-43771
Type: osv

## Details
In nqptp-message-handlers.c in nqptp before 1.2.3, crafted packets received on the control port could crash the program.

## References
- https://github.com/mikebrady/nqptp/releases/tag/1.2.3
- https://github.com/mikebrady/nqptp/releases/tag/1.2.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43771.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-43771
- https://github.com/mikebrady/nqptp/commit/b24789982d5cc067ecf6e8f3352b701d177530ec
