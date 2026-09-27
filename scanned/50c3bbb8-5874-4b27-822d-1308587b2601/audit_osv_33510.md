# [H] CVE-2025-44952

## Summary
Severity: High
Advisory: CVE-2025-44952
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-44952
Type: osv

## Details
A missing length check in `ogs_pfcp_subnet_add` function from PFCP library, used by both smf and upf in open5gs 2.7.2 and earlier, allows a local attacker to cause a Buffer Overflow by changing the `session.dnn` field with a value with length greater than 101.

## References
- https://gist.github.com/scemodicecosa/8643fbfc9490f40e955e9f9e9b0d9077
- https://gist.github.com/scmdcs/8643fbfc9490f40e955e9f9e9b0d9077
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/44xxx/CVE-2025-44952.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-44952
- https://github.com/open5gs/open5gs/issues/3775
