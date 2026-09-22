# [M] NodeBB - ActivityPub Author Spoofing via Unvalidated attributedTo Mapped to Local User

## Summary
Severity: Medium
Advisory: CVE-2026-58593
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-58593
Type: osv

## Details
NodeBB does not bind the claimed author of an inbound ActivityPub object to the authenticated remote actor. The inbound middleware verifies the HTTP-signature actor and checks the origin of object.id, but never validates that attributedTo corresponds to the sender. In the object mock, attributedTo is used directly as a uid, and actors.assert silently ignores numeric identifiers (filtering them out without re-deriving the uid), so a federated remote actor can set attributedTo to a bare numeric value such as 1 and have the resulting post or private message created with that local uid as author, including the administrator account. This lets a remote attacker forge posts and direct messages attributed to arbitrary local users. Requires the ActivityPub/federation feature to be enabled.

## References
- https://github.com/NodeBB/NodeBB/blob/v4.13.2/src/activitypub/mocks.js
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58593.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58593
- https://www.vulncheck.com/advisories/nodebb-activitypub-author-spoofing-via-unvalidated-attributedto-mapped-to-local-user
- https://github.com/bikini/exploitarium/tree/main/nodebb-activitypub-attributedto-local-uid-spoof-poc
