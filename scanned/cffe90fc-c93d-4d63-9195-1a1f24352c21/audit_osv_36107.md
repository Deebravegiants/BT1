# [M] CVE-2026-20731

## Summary
Severity: Medium
Advisory: CVE-2026-20731
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-20731
Type: osv

## Details
Improper buffer restrictions for the Intel(R) NPU Driver for all versions within Ring 3: User Applications may allow a denial of service. Unprivileged software adversary with an authenticated user combined with a low complexity attack may enable denial of service. This result may potentially occur via local access when attack requirements are not present without special internal knowledge and requires no user interaction. The potential vulnerability may impact the confidentiality (none), integrity (low) and availability (high) of the vulnerable system, resulting in subsequent system confidentiality (none), integrity (none) and availability (none) impacts.

## References
- https://intel.com/content/www/us/en/security-center/advisory/intel-sa-01456.html
