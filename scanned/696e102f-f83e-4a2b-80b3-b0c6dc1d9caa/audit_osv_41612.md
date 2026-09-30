# [M] libheif: Reachable assertion in HeifContext::get_track() aborts on a valid-but-empty HEIF sequence file (context.cc:2110)

## Summary
Severity: Medium
Advisory: CVE-2026-62377
Aliases: GHSA-9ww4-9v47-m7pj
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-62377
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. In 1.23.0 and earlier, a crafted HEIF sequence accepted by heif_context_read_from_memory() can leave the context with no registered sequence tracks and crash when heif_context_get_track(ctx, 0) is called. HeifContext::get_track() in libheif/context.cc executes assert(has_sequence()) before its normal error handling, so assert-enabled builds abort instead of allowing the public wrapper in libheif/api/libheif/heif_sequences.cc to return null. In release builds, removing the assertion lets the track_id zero path dereference m_tracks.begin()->second on an empty map, which is undefined behavior and typically crashes. The issue is reachable through documented public APIs after parsing attacker-controlled bytes. This issue is fixed in version 1.23.1.

## References
- https://github.com/strukturag/libheif/releases/tag/v1.23.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62377.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-9ww4-9v47-m7pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-62377
- https://github.com/strukturag/libheif/issues/1844
- https://github.com/strukturag/libheif/commit/e1a0bc1c1ae74f8075eaca30a1cdb2b9bee698d3
