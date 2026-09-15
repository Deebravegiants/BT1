# [M] Glib: path traversal in glib/gio/gdbusauthmechanismsha1.c via keyring_lookup_entry and mechanism_client_data_receive

## Summary
Severity: Medium
Advisory: CVE-2026-58015
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58015
Type: osv

## Details
A flaw was found in GLib. The D-Bus client-side implementation of the DBUS_COOKIE_SHA1 SASL authentication mechanism does not validate the cookie_context parameter received from the server. A malicious D-Bus server can supply a cookie_context containing path traversal sequences, causing the client to read an arbitrary file and exfiltrate sensitive data by verifying guessed file contents against a generated hash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:49512
- https://access.redhat.com/errata/RHSA-2026:55440
- https://access.redhat.com/errata/RHSA-2026:57015
- https://access.redhat.com/errata/RHSA-2026:58981
- https://access.redhat.com/errata/RHSA-2026:61766
- https://access.redhat.com/errata/RHSA-2026:61783
- https://access.redhat.com/errata/RHSA-2026:63135
- https://access.redhat.com/errata/RHSA-2026:63138
- https://access.redhat.com/errata/RHSA-2026:63140
- https://access.redhat.com/errata/RHSA-2026:65762
- https://access.redhat.com/errata/RHSA-2026:65763
- https://access.redhat.com/errata/RHSA-2026:65767
- https://access.redhat.com/errata/RHSA-2026:65768
- https://access.redhat.com/errata/RHSA-2026:65769
- https://access.redhat.com/errata/RHSA-2026:65770
- https://access.redhat.com/errata/RHSA-2026:65771
- https://access.redhat.com/errata/RHSA-2026:65773
- https://access.redhat.com/errata/RHSA-2026:66018
