# [H] CVE-2025-44951

## Summary
Severity: High
Advisory: CVE-2025-44951
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-44951
Type: osv

## Details
A missing length check in `ogs_pfcp_dev_add` function from PFCP library, used by both smf and upf in open5gs 2.7.2 and earlier, allows a local attacker to cause a Buffer Overflow by changing the `session.dev` field with a value with length greater than 32.

## References
- https://gist.github.com/scmdcs/6d878d6074f0e2f4a8fb69e9864068b7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/44xxx/CVE-2025-44951.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-44951
- https://github.com/open5gs/open5gs/issues/3775
- https://github.com/open5gs/open5gs/commit/e3dd98cd291fba233a46adb2881213fc6e38b924
