# [H] Planet's secret file is created with excessive permissions

## Summary
Severity: High
Advisory: GHSA-j5fj-rfh6-qj85
CVE: CVE-2023-32303
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-12
Source: https://github.com/advisories/GHSA-j5fj-rfh6-qj85
Type: github-advisory

## Affected
- PyPI: `planet` — affected >=0 <2.0.1

## Details
### Impact
The secret file stores the user's Planet API authentication information. It should only be accessible by the user, but its permissions allowed the user's group and non-group to read the file as well. 

### Validation
Check the permissions on the secret file with `ls -l ~/.planet.json` and ensure that they read as `-rw-------`

### Patches
[d71415a8](https://github.com/planetlabs/planet-client-python/commit/d71415a83119c5e89d7b80d5f940d162376ee3b7)

### Workarounds
Set the secret file permissions to only user read/write by hand:
```
chmod 600 ~/.planet.json
```

## References
- https://github.com/planetlabs/planet-client-python/security/advisories/GHSA-j5fj-rfh6-qj85
- https://nvd.nist.gov/vuln/detail/CVE-2023-32303
- https://github.com/planetlabs/planet-client-python/commit/d71415a83119c5e89d7b80d5f940d162376ee3b7
- https://github.com/planetlabs/planet-client-python
- https://github.com/planetlabs/planet-client-python/releases/tag/2.0.1
- https://github.com/pypa/advisory-database/tree/main/vulns/planet/PYSEC-2023-71.yaml
