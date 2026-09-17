# [M] CVE-2025-48964

## Summary
Severity: Medium
Advisory: CVE-2025-48964
Aliases: GHSA-25fr-jw29-74f9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-48964
Type: osv

## Details
ping in iputils before 20250602 allows a denial of service (application error in adaptive ping mode or incorrect data collection) via a crafted ICMP Echo Reply packet, because a zero timestamp can lead to large intermediate values that have an integer overflow when squared during statistics calculations. NOTE: this issue exists because of an incomplete fix for CVE-2025-47268 (that fix was only about timestamp calculations, and it did not account for a specific scenario where the original timestamp in the ICMP payload is zero).

## References
- https://github.com/iputils/iputils/issues
- https://github.com/iputils/iputils/releases/tag/20250602
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48964.json
- https://github.com/iputils/iputils/security/advisories/GHSA-25fr-jw29-74f9
- https://nvd.nist.gov/vuln/detail/CVE-2025-48964
- https://bugzilla.suse.com/show_bug.cgi?id=1243772
- https://github.com/iputils/iputils/commit/afa36390394a6e0cceba03b52b59b6d41710608c
