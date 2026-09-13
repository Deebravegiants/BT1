# [H] CVE-2026-52023

## Summary
Severity: High
Advisory: CVE-2026-52023
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-52023
Type: osv

## Details
An issue in kamailio v.6.1.1 and before allows a remote attacker to cause a denial of service via the ims_registrar_pcscf module, specifically the pcscf_save_pending/save_pending path and security-agreement parsing in sec_agree.c:parse_sec_agree()

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52023.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52023
- https://github.com/kamailio/kamailio/issues/4671
- https://github.com/kamailio/kamailio/commit/722c06b3efc53ccb369ce812c685c7d069508187
