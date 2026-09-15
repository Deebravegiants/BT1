# [C] hermes-management is vulnerable to RCE due to Apache commons-jxpath

## Summary
Severity: Critical
Advisory: GHSA-2gh6-wc3m-g37f
CWE: CWE-1395
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-2gh6-wc3m-g37f
Type: github-advisory

## Affected
- Maven: `pl.allegro.tech.hermes:hermes-management` — affected >=0.8.2 <2.2.9

## Details
### Impact
hermes-management is vulnerable to RCE when it processes user-controlled data due to using Apache commons-jxpath.

### Patches
Upgrade Hermes to at least hermes-2.2.9

### References
https://hackinglab.cz/en/blog/remote-code-execution-in-jxpath-library-cve-2022-41852/

## References
- https://github.com/allegro/hermes/security/advisories/GHSA-2gh6-wc3m-g37f
- https://github.com/allegro/hermes/commit/72ecc5aa41e37fd614443dd35d9200b66a61afb1
- https://github.com/allegro/hermes/commit/92d4ad0cf6868ba784707772b78e129fedff7a31
- https://github.com/allegro/hermes
- https://hackinglab.cz/en/blog/remote-code-execution-in-jxpath-library-cve-2022-41852
