# [M] CVE-2022-3676

## Summary
Severity: Medium
Advisory: CVE-2022-3676
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-10-24
Source: https://osv.dev/vulnerability/CVE-2022-3676
Type: osv

## Details
In Eclipse Openj9 before version 0.35.0, interface calls can be inlined without a runtime type check. Malicious bytecode could make use of this inlining to access or modify memory via an incompatible type.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3676.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3676
- https://gitlab.eclipse.org/eclipsefdn/emo-team/emo/-/issues/389
- https://github.com/eclipse-openj9/openj9/pull/16122
- https://github.com/eclipse/omr/pull/6773
