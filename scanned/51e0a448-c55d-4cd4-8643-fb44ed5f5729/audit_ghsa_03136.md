# [H] GPGME Go wrapper contains Use After Free

## Summary
Severity: High
Advisory: GHSA-m6wg-2mwg-4rfq
CVE: CVE-2020-8945
CWE: CWE-416
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-m6wg-2mwg-4rfq
Type: github-advisory

## Affected
- Go: `github.com/proglottis/gpgme` — affected >=0 <0.1.1

## Details
The proglottis Go wrapper before 0.1.1 for the GPGME library has a use-after-free, as demonstrated by use for container image pulls by Docker or CRI-O. This leads to a crash or potential code execution during GPG signature verification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8945
- https://github.com/proglottis/gpgme/pull/23
- https://github.com/containers/image/commit/4c7a23f82ef09127b0ff28366d1cf31316dd6cc1
- https://github.com/proglottis/gpgme/commit/92153bcb59bd2f511e502262c46c7bd660e21733
- https://access.redhat.com/errata/RHSA-2020:0679
- https://access.redhat.com/errata/RHSA-2020:0689
- https://access.redhat.com/errata/RHSA-2020:0697
- https://bugzilla.redhat.com/show_bug.cgi?id=1795838
- https://github.com/proglottis/gpgme
- https://github.com/proglottis/gpgme/compare/v0.1.0...v0.1.1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3SOCLOPTSYABTE4CLTSPDIFE6ZZZR4LX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/H6P6SSNKN4H6GSEVROHBDXA64PX7EOED
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KDBT77KV3U7BESJX3P4S4MPVDGRTAQA2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WXV7NZELYWRRCXATXU3FYD3G3WJT3WYM
- https://pkg.go.dev/vuln/GO-2021-0096
