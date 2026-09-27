# [M] Use after free in libwebp

## Summary
Severity: Medium
Advisory: CVE-2023-1999
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-20
Source: https://osv.dev/vulnerability/CVE-2023-1999
Type: osv

## Details
There exists a use after free/double free in libwebp. An attacker can use the ApplyFiltersAndEncode() function and loop through to free best.bw and assign best = trial pointer. The second loop will then return 0 because of an Out of memory error in VP8 encoder, the pointer is still assigned to trial and the AddressSanitizer will attempt a double free.

## References
- https://chromium.googlesource.com/
- https://chromium.googlesource.com/webm/libwebp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1999.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1999
- https://security.gentoo.org/glsa/202309-05
