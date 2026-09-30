# [M] CVE-2024-49394

## Summary
Severity: Medium
Advisory: CVE-2024-49394
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-11-12
Source: https://osv.dev/vulnerability/CVE-2024-49394
Type: osv

## Details
In mutt and neomutt the In-Reply-To email header field is not protected by cryptographic signing which allows an attacker to reuse an unencrypted but signed email message to impersonate the original sender.

## References
- https://access.redhat.com/security/cve/CVE-2024-49394
- https://bugzilla.redhat.com/show_bug.cgi?id=2325330
