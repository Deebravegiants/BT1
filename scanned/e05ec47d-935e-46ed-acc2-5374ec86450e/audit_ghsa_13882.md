# [H] ecdh vulnerable to Exposure of Resource to Wrong Sphere

## Summary
Severity: High
Advisory: GHSA-p2hp-3wv3-4w74
CVE: CVE-2022-44310
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-24
Source: https://github.com/advisories/GHSA-p2hp-3wv3-4w74
Type: github-advisory

## Affected
- npm: `ecdh` — affected >=0 <0.2.0

## Details
In Development IL ecdh before 0.2.0, an attacker can send an invalid point (not on the curve) as the public key, and obtain the derived shared secret.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-44310
- https://github.com/developmentil/ecdh/issues/3
- https://github.com/developmentil/ecdh/pull/4
- https://github.com/developmentil/ecdh/commit/ef4560e7233f4e8107a17a77bc540121599c78fa
- https://github.com/developmentil/ecdh
