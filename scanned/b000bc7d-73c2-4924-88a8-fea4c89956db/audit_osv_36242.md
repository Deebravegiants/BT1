# [M] Suricata datasets: stack overflow when saving a set

## Summary
Severity: Medium
Advisory: CVE-2026-22262
Aliases: GHSA-9qg5-2gwh-xp86
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-22262
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. While saving a dataset a stack buffer is used to prepare the data. Prior to versions 8.0.3 and 7.0.14, if the data in the dataset is too large, this can result in a stack overflow. Versions 8.0.3 and 7.0.14 contain a patch. As a workaround, do not use rules with datasets `save` nor `state` options.

## References
- https://redmine.openinfosecfoundation.org/issues/8110
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22262.json
- https://github.com/OISF/suricata/security/advisories/GHSA-9qg5-2gwh-xp86
- https://nvd.nist.gov/vuln/detail/CVE-2026-22262
- https://github.com/OISF/suricata/commit/0eff24213763c2aa2bb0957901d5dc1e18414dbf
- https://github.com/OISF/suricata/commit/27a2180bceaa3477419c78c54fce364398d011f1
- https://github.com/OISF/suricata/commit/32609e6896f9079c175665a94005417cec7637eb
- https://github.com/OISF/suricata/commit/32a1b9ae6aa80a60c073897e38a2ac6ea0f64521
- https://github.com/OISF/suricata/commit/d6bc718e303ecbec5999066b8bc88eeeca743658
- https://github.com/OISF/suricata/commit/d767dfadcd166f82683757818b9e46943326ac90
