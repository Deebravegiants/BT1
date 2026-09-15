# [H] Gnutls: gnutls: denial of service via dtls zero-length fragment

## Summary
Severity: High
Advisory: CVE-2026-33845
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-33845
Type: osv

## Details
A flaw in GnuTLS DTLS handshake parsing allows malformed fragments with zero length and non-zero offset, leading to an integer underflow during reassembly and resulting in an out-of-bounds read. This issue is remotely exploitable and may cause information disclosure or denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33845.json
- https://access.redhat.com/errata/RHSA-2026:13274
- https://access.redhat.com/errata/RHSA-2026:20611
- https://access.redhat.com/errata/RHSA-2026:20612
- https://access.redhat.com/errata/RHSA-2026:20613
- https://access.redhat.com/errata/RHSA-2026:26319
- https://access.redhat.com/errata/RHSA-2026:26409
- https://access.redhat.com/errata/RHSA-2026:29197
- https://access.redhat.com/errata/RHSA-2026:30004
- https://access.redhat.com/errata/RHSA-2026:30849
- https://access.redhat.com/errata/RHSA-2026:30850
- https://access.redhat.com/errata/RHSA-2026:32962
- https://access.redhat.com/errata/RHSA-2026:33125
- https://access.redhat.com/errata/RHSA-2026:34372
- https://access.redhat.com/errata/RHSA-2026:36004
- https://access.redhat.com/errata/RHSA-2026:36005
- https://access.redhat.com/errata/RHSA-2026:36006
- https://access.redhat.com/errata/RHSA-2026:41921
