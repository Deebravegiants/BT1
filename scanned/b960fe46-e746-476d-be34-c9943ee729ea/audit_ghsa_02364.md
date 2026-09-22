# [C] Double-free in id-map

## Summary
Severity: Critical
Advisory: GHSA-8gmx-cpcg-f8h5
CVE: CVE-2021-30455
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8gmx-cpcg-f8h5
Type: github-advisory

## Affected
- crates.io: `id-map` — affected >=0

## Details
The clone_from implementation for IdMap drops the values present in the map and then begins cloning values from the other map. If a .clone() call pancics, then the afformentioned dropped elements can be freed again.
get_or_insert

get_or_insert reserves space for a value, before calling the user provided insertion function f. If the function f panics then uninitialized or previously freed memory can be dropped.
remove_set

When removing a set of elements, ptr::drop_in_place is called on each of the element to be removed. If the Drop impl of one of these elements panics then the previously dropped elements can be dropped again.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30455
- https://github.com/andrewhickman/id-map/issues/3
- https://github.com/andrewhickman/id-map
- https://rustsec.org/advisories/RUSTSEC-2021-0052.html
