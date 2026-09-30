# [M] Ouch! allows a segmentation fault due to use of uninitialized memory

## Summary
Severity: Medium
Advisory: GHSA-2wq5-g96f-mv3v
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-09-23
Source: https://github.com/advisories/GHSA-2wq5-g96f-mv3v
Type: github-advisory

## Affected
- crates.io: `ouch` — affected >=0 <0.3.1

## Details
When trying to decompress a file using "ouch", we can reach the function "ouch::archive::zip::convert_zip_date_time". In the function, there is a unsafe function, "transmute". Once the "transmute" function is called to convert the type of "month" object, the address of the object is changed to the uninitialized memory region. After that, when other function tries to dereference "month", segmentation fault occurs.

## References
- https://github.com/ouch-org/ouch/issues/707
- https://github.com/ouch-org/ouch
- https://rustsec.org/advisories/RUSTSEC-2024-0374.html
