# [M] Confidential Containers Guest Components image-rs: zip-slip-class arbitrary file write via absolute entry path in hardlink fallback

## Summary
Severity: Medium
Advisory: CVE-2026-47699
Aliases: GHSA-84rc-2q4r-45pc
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-47699
Type: osv

## Details
Confidential Containers Guest Components provides guest tools and components for confidential container workloads. From 0.16.0 until 0.20.0, a crafted OCI image layer can make image_rs::stream::unpack::unpack() create a hardlink outside its destination directory. In image-rs/src/stream/unpack.rs, try_hardlink_fallback() validates the hardlink source but computes the destination with destination.join(&entry_rel). Rust Path::join replaces the base when entry_rel is an absolute tar entry path, so fs::hard_link(&src_canon, &dst_entry_abs) can write attacker-controlled content to an arbitrary absolute path. In Confidential Containers the workload owner already controls trusted image content, so the issue is a workload-owner escape into the pod virtual machine rather than a crossing of the image trust boundary, but it may enable access to pod virtual machine capabilities and attestation abuse. This issue is fixed in version 0.20.0.

## References
- https://github.com/confidential-containers/guest-components/releases/tag/v0.20.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47699.json
- https://github.com/confidential-containers/guest-components/security/advisories/GHSA-84rc-2q4r-45pc
- https://nvd.nist.gov/vuln/detail/CVE-2026-47699
- https://github.com/confidential-containers/guest-components/commit/14fbb711af0b29bb9cad307969d57b0de9b85d7f
- https://github.com/confidential-containers/guest-components/commit/7cc1bc458973310296e58aedbb15cb7963297bbe
- https://github.com/confidential-containers/guest-components/pull/1440
- https://github.com/confidential-containers/guest-components/pull/1457
