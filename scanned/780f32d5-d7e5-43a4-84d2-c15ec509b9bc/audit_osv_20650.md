# [M] CVE-2021-3565

## Summary
Severity: Medium
Advisory: CVE-2021-3565
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-04
Source: https://osv.dev/vulnerability/CVE-2021-3565
Type: osv

## Details
A flaw was found in tpm2-tools in versions before 5.1.1 and before 4.3.2. tpm2_import used a fixed AES key for the inner wrapper, potentially allowing a MITM attacker to unwrap the inner portion and reveal the key being imported. The highest threat from this vulnerability is to data confidentiality.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ESY6HRYUKR5ZG2K5QAJQC5S6HMKZMFK7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XK5M7I66PBXSN663TSLAZ3V6TWWFCV7C/
- https://bugzilla.redhat.com/show_bug.cgi?id=1964427
