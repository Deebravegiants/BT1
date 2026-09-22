# [M] Blinko 1.8.7 Cross-User Private Note Disclosure via noteReferenceList

## Summary
Severity: Medium
Advisory: CVE-2026-85624
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85624
Type: osv

## Details
Blinko 1.8.7 contains a cross-user private note disclosure vulnerability in the noteReferenceList procedure that performs no ownership verification on supplied note identifiers. Authenticated attackers can enumerate sequential note IDs and retrieve complete content of other users' private notes including attachments and tags.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85624.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85624
- https://www.vulncheck.com/advisories/blinko-1.8.7-cross-user-private-note-disclosure-via-notereferencelist
- https://github.com/blinkospace/blinko/issues/1217
- https://github.com/blinkospace/blinko
- https://github.com/blinkospace/blinko/blob/1.8.8/server/routerTrpc/note.ts
