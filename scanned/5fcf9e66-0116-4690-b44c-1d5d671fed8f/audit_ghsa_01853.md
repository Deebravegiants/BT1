# [H] An issue in Atomix v3.1.5 allows unauthorized Atomix nodes to become the lead node.

## Summary
Severity: High
Advisory: GHSA-4jhc-wjr3-pwh2
CVE: CVE-2020-35211
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-12-17
Source: https://github.com/advisories/GHSA-4jhc-wjr3-pwh2
Type: github-advisory

## Affected
- Maven: `io.atomix:atomix` — affected >=0

## Details
An issue in Atomix v3.1.5 allows unauthorized Atomix nodes to become the lead node in a target cluster via manipulation of the variable terms in RaftContext.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35211
- https://docs.google.com/presentation/d/1C_IpRfSU-9FMezcHCFZ-qg-15JO-W36yvqcnzI8sQs8/edit?usp=sharing
- https://github.com/atomix/atomix
