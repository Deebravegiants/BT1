# [C] CVE-2021-3406

## Summary
Severity: Critical
Advisory: CVE-2021-3406
Aliases: GHSA-78f8-6c68-375m
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-25
Source: https://osv.dev/vulnerability/CVE-2021-3406
Type: osv

## Details
A flaw was found in keylime 5.8.1 and older. The issue in the Keylime agent and registrar code invalidates the cryptographic chain of trust from the Endorsement Key certificate to agent attestations.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YAWKEF2LVXUME266T6RNRVBGAD375QAT/
- https://github.com/keylime/keylime/security/advisories/GHSA-78f8-6c68-375m
- https://bugzilla.redhat.com/show_bug.cgi?id=1932469
