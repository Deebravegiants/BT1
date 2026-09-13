# [H] 389-ds-base: 389-ds-base: heap buffer overflow in sasl_io_recv() via padded sasl unbind

## Summary
Severity: High
Advisory: CVE-2026-11610
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-11610
Type: osv

## Details
A heap buffer overflow flaw was found in the SASL I/O layer of 389 Directory Server
(389-ds-base). After a successful SASL bind with integrity protection (SSF > 0),
an authenticated attacker can send a specially crafted oversized LDAP UNBIND packet
that is copied into a 512-byte heap receive buffer without a bounds check in
sasl_io_recv() in sasl_io.c. This allows up to approximately 2 megabytes of
attacker-controlled data to overflow the buffer, causing a denial of service (server
crash). In FreeIPA and Red Hat Identity Management deployments, any domain user with
a valid Kerberos ticket, any enrolled host, or any service account can trigger this
vulnerability over the network after authenticating via GSSAPI.
The vulnerable code path has existed since approximately 2013 (389-ds-base 1.3.2) and
was not addressed by the CVE-2025-14905 fix, which patched a separate heap overflow
in schema.c only.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:36195
- https://access.redhat.com/errata/RHSA-2026:36196
- https://access.redhat.com/errata/RHSA-2026:36197
- https://access.redhat.com/errata/RHSA-2026:36198
- https://access.redhat.com/errata/RHSA-2026:36200
- https://access.redhat.com/errata/RHSA-2026:36201
- https://access.redhat.com/errata/RHSA-2026:36202
- https://access.redhat.com/errata/RHSA-2026:36204
- https://access.redhat.com/errata/RHSA-2026:36205
- https://access.redhat.com/errata/RHSA-2026:36206
- https://access.redhat.com/errata/RHSA-2026:36208
- https://access.redhat.com/errata/RHSA-2026:36209
- https://access.redhat.com/errata/RHSA-2026:36585
- https://access.redhat.com/errata/RHSA-2026:36641
- https://access.redhat.com/errata/RHSA-2026:36660
- https://access.redhat.com/errata/RHSA-2026:36670
- https://access.redhat.com/errata/RHSA-2026:36671
- https://access.redhat.com/security/cve/CVE-2026-11610
