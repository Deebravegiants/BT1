# [H] CVE-2025-58145

## Summary
Severity: High
Advisory: CVE-2025-58145
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-58145
Type: osv

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

There are two issues related to the mapping of pages belonging to other
domains: For one, an assertion is wrong there, where the case actually
needs handling.  A NULL pointer de-reference could result on a release
build.  This is CVE-2025-58144.

And then the P2M lock isn't held until a page reference was actually
obtained (or the attempt to do so has failed).  Otherwise the page can
not only change type, but even ownership in between, thus allowing
domain boundaries to be violated.  This is CVE-2025-58145.

## References
- http://www.openwall.com/lists/oss-security/2025/09/09/2
- http://xenbits.xen.org/xsa/advisory-473.html
- https://xenbits.xenproject.org/xsa/advisory-473.html
