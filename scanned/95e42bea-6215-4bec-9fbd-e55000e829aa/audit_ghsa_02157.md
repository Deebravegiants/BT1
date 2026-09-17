# [H] Data races in rocket

## Summary
Severity: High
Advisory: GHSA-8q2v-67v7-6vc6
CVE: CVE-2020-35882
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8q2v-67v7-6vc6
Type: github-advisory

## Affected
- crates.io: `rocket` — affected >=0.4.0 <0.4.5

## Details
The affected version of rocket contains a Clone trait implementation of LocalRequest that reuses the pointer to inner Request object. This causes data race in rare combinations of APIs if the original and the cloned objects are modified at the same time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35882
- https://github.com/SergioBenitez/Rocket/issues/1312
- https://github.com/SergioBenitez/Rocket
- https://rustsec.org/advisories/RUSTSEC-2020-0028.html
