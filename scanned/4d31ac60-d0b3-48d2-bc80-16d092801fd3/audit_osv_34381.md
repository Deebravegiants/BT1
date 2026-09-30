# [M] Libarchive: heap buffer over read in copy_from_lzss_window() at archive_read_support_format_rar.c

## Summary
Severity: Medium
Advisory: CVE-2025-5915
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:H)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-5915
Type: osv

## Details
A vulnerability has been identified in the libarchive library. This flaw can lead to a heap buffer over-read due to the size of a filter block potentially exceeding the Lempel-Ziv-Storer-Schieber (LZSS) window. This means the library may attempt to read beyond the allocated memory buffer, which can result in unpredictable program behavior, crashes (denial of service), or the disclosure of sensitive information from adjacent memory regions.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/libarchive/libarchive/
- https://github.com/libarchive/libarchive/releases/tag/v3.8.0
- https://access.redhat.com/security/cve/CVE-2025-5915
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5915.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5915
- https://bugzilla.redhat.com/show_bug.cgi?id=2370865
- https://github.com/libarchive/libarchive/pull/2599
