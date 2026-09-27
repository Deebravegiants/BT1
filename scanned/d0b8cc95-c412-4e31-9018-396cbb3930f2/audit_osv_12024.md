# [M] CVE-2018-1000664

## Summary
Severity: Medium
Advisory: CVE-2018-1000664
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-1000664
Type: osv

## Details
daneren2005 DSub for Subsonic (Android client) version 5.4.1 contains a CWE-295: Improper Certificate Validation vulnerability in HTTPS Client that can result in Any non-CA signed server certificate, including self signed and expired, are accepted by the client. This attack appear to be exploitable via The victim connects to a server that's MITM/Proxied by an attacker.

## References
- https://github.com/daneren2005/Subsonic/issues/60
