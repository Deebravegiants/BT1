# [H] CVE-2023-2911

## Summary
Severity: High
Advisory: CVE-2023-2911
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-21
Source: https://osv.dev/vulnerability/CVE-2023-2911
Type: osv

## Details
If the `recursive-clients` quota is reached on a BIND 9 resolver configured with both `stale-answer-enable yes;` and `stale-answer-client-timeout 0;`, a sequence of serve-stale-related lookups could cause `named` to loop and terminate unexpectedly due to a stack overflow.
This issue affects BIND 9 versions 9.16.33 through 9.16.41, 9.18.7 through 9.18.15, 9.16.33-S1 through 9.16.41-S1, and 9.18.11-S1 through 9.18.15-S1.

## References
- https://kb.isc.org/docs/cve-2023-2911
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SEFCEVCTYEMKTWA7V7EYPI5YQQ4JWDLI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U3K6AJK7RRSR53HRF5GGKPA6PDUDWOD2/
- https://security.netapp.com/advisory/ntap-20230703-0010/
- https://www.debian.org/security/2023/dsa-5439
- http://www.openwall.com/lists/oss-security/2023/06/21/6
