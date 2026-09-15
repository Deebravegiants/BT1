# [H] CVE-2024-44069

## Summary
Severity: High
Advisory: CVE-2024-44069
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-08-19
Source: https://osv.dev/vulnerability/CVE-2024-44069
Type: osv

## Details
Pi-hole before 6 allows unauthenticated admin/api.php?setTempUnit= calls to change the temperature units of the web dashboard. NOTE: the supplier reportedly does "not consider the bug a security issue" but the specific motivation for letting arbitrary persons change the value (Celsius, Fahrenheit, or Kelvin), seen by the device owner, is unclear.

## References
- https://www.kiyell.com/The-Harmless-Pihole-Bug/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44069.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44069
- https://github.com/pi-hole/web/pull/3077
