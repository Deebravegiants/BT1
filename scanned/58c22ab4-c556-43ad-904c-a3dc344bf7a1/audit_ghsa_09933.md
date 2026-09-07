# [H] Nest Affected by DoS via Recursive handleData in JsonSocket (TCP Transport)

## Summary
Severity: High
Advisory: GHSA-hpwf-8g29-85qm
CVE: CVE-2026-40879
CWE: CWE-674, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-hpwf-8g29-85qm
Type: github-advisory

## Affected
- npm: `@nestjs/microservices` — affected >=0 <11.1.19

## Details
### Impact
Attacker sends many small, valid JSON messages in one TCP frame
 → handleData() recurses once per message; buffer shrinks each call
 → maxBufferSize is never reached; call stack overflows instead
 → A ~47 KB payload is sufficient to trigger RangeError

### Patches

Fixed in `@nestjs/microservices@11.1.19`

### References

Discovered by https://github.com/hwpark6804-gif

## References
- https://github.com/nestjs/nest/security/advisories/GHSA-hpwf-8g29-85qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-40879
- https://github.com/nestjs/nest
