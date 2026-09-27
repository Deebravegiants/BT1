# [M] CVE-2026-20913

## Summary
Severity: Medium
Advisory: CVE-2026-20913
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-20913
Type: osv

## Details
Improper input validation for some Intel(R) Neural Compressor software before version v3.7 within Ring 3: User Applications may allow an escalation of privilege. Unprivileged software adversary with an authenticated user combined with a low complexity attack may enable escalation of privilege. This result may potentially occur via local access when attack requirements are not present without special internal knowledge and requires no user interaction. The potential vulnerability may impact the confidentiality (low), integrity (low) and availability (low) of the vulnerable system, resulting in subsequent system confidentiality (none), integrity (none) and availability (none) impacts.

## References
- https://intel.com/content/www/us/en/security-center/advisory/intel-sa-01454.html
