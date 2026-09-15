# [H] CVE-2023-48011

## Summary
Severity: High
Advisory: CVE-2023-48011
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-11-15
Source: https://osv.dev/vulnerability/CVE-2023-48011
Type: osv

## Details
GPAC v2.3-DEV-rev566-g50c2ab06f-master was discovered to contain a heap-use-after-free via the flush_ref_samples function at /gpac/src/isomedia/movie_fragments.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48011.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-48011
- https://github.com/gpac/gpac/issues/2611
- https://github.com/gpac/gpac/commit/c70f49dda4946d6db6aa55588f6a756b76bd84ea
