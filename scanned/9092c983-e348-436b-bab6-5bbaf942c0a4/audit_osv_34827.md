# [H] CVE-2025-65503

## Summary
Severity: High
Advisory: CVE-2025-65503
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-65503
Type: osv

## Details
Use after free in endpoint destructors in Redboltz async_mqtt 10.2.5 allows local users to cause a denial of service via triggering SSL initialization failure that results in incorrect destruction order between io_context and endpoint objects.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65503.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65503
- https://github.com/redboltz/async_mqtt/issues/436
- https://github.com/redboltz/async_mqtt/pull/437
