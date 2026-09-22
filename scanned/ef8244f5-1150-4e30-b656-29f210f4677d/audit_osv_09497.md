# [C] CVE-2017-0889

## Summary
Severity: Critical
Advisory: CVE-2017-0889
Aliases: GHSA-5jcf-c5rg-rmm8
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-13
Source: https://osv.dev/vulnerability/CVE-2017-0889
Type: osv

## Details
Paperclip ruby gem version 3.1.4 and later suffers from a Server-SIde Request Forgery (SSRF) vulnerability in the Paperclip::UriAdapter class. Attackers may be able to access information about internal network resources.

## References
- https://hackerone.com/reports/209430
- https://hackerone.com/reports/713
- https://github.com/thoughtbot/paperclip/pull/2435
