# [M] CVE-2020-6804

## Summary
Severity: Medium
Advisory: CVE-2020-6804
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-02-28
Source: https://osv.dev/vulnerability/CVE-2020-6804
Type: osv

## Details
A reflected XSS vulnerability exists within the gateway, allowing an attacker to craft a specialized URL which could steal the user's authentication token. When combined with CVE-2020-6803, an attacker could fully compromise the system.

## References
- https://github.com/mozilla-iot/gateway/pull/2446
