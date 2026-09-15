# [C] Authentication bypass in MAGMI

## Summary
Severity: Critical
Advisory: GHSA-g475-pch5-6wvv
CVE: CVE-2020-5777
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-g475-pch5-6wvv
Type: github-advisory

## Affected
- Packagist: `dweeves/magmi` — affected >=0 <0.7.24

## Details
MAGMI versions prior to 0.7.24 are vulnerable to a remote authentication bypass due to allowing default credentials in the event there is a database connection failure. A remote attacker can trigger this connection failure if the Mysql setting max_connections (default 151) is lower than Apache (or another web server) setting MaxRequestWorkers (formerly MaxClients) (default 256). This can be done by sending at least 151 simultaneous requests to the Magento website to trigger a "Too many connections" error, then use default magmi:magmi basic authentication to remotely bypass authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5777
- https://github.com/dweeves/magmi-git/commit/dde71de5cfd505fe78e5caf21d6531b61450a16f
- https://www.tenable.com/security/research/tra-2020-51
