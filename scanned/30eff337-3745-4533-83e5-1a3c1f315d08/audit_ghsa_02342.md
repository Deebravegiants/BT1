# [C] Double-free in id-map

## Summary
Severity: Critical
Advisory: GHSA-rccq-j2m7-8fwr
CVE: CVE-2021-30457
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rccq-j2m7-8fwr
Type: github-advisory

## Affected
- crates.io: `id-map` — affected >=0

## Details
A double free can occur in remove_set upon a panic in a Drop impl. When removing a set of elements, ptr::drop_in_place is called on each of the element to be removed. If the Drop impl of one of these elements panics then the previously dropped elements can be dropped again.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30457
- https://github.com/andrewhickman/id-map/issues/3
- https://github.com/andrewhickman/id-map
- https://rustsec.org/advisories/RUSTSEC-2021-0052.html
