# [H] MobSF vulnerability allows SSRF due to the allow_redirects=True parameter

## Summary
Severity: High
Advisory: GHSA-m435-9v6r-v5f6
CVE: CVE-2024-54000
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-27
Source: https://github.com/advisories/GHSA-m435-9v6r-v5f6
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <3.9.7

## Details
### Summary
The fix for the "SSRF Vulnerability on assetlinks_check(act_name, well_knowns)" vulnerability could potentially be bypassed.

### Details
Since the requests.get() request in the _check_url method is specified as allow_redirects=True, if "https://mydomain.com/.well-known/assetlinks.json" returns a 302 redirect, subsequent requests will be sent automatically. If the redirect location is "http://192.168.1.102/user/delete/1", a request will be sent here as well.

<img width="610" alt="image" src="https://github.com/MobSF/Mobile-Security-Framework-MobSF/assets/150332295/a8c9630e-3d12-441a-816c-8f5e427a5194">

It will be safer to use allow_redirects=False.

### Impact
The attacker can cause the server to make a connection to internal-only services within the organization's infrastructure.

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-m435-9v6r-v5f6
- https://nvd.nist.gov/vuln/detail/CVE-2024-54000
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/f22c584aa7d43527970c9da61eb678953cfc0a8e
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
- https://github.com/pypa/advisory-database/tree/main/vulns/mobsf/PYSEC-2024-256.yaml
