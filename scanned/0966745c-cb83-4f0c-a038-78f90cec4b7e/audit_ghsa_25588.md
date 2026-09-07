# [M] Cross-site Scripting in xain

## Summary
Severity: Medium
Advisory: GHSA-5chx-gg25-v37m
CVE: CVE-2018-20302
CWE: CWE-79
Ecosystem: Hex
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-5chx-gg25-v37m
Type: github-advisory

## Affected
- Hex: `xain` — affected >=0 <0.6.2

## Details
XSS is possible via the use of the order query parameter. An example request
  would look like:
  ```
  http://host/ressources?order=%27><script>alert(1);</script>
  ```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20302
- https://github.com/smpallen99/xain/issues/18
- https://github.com/dependabot/elixir-security-advisories/blob/master/packages/xain/2018-09-03.yml
- https://github.com/smpallen99/xain
