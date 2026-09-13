# [H] openmls has improper tag validation

## Summary
Severity: High
Advisory: GHSA-8x3w-qj7j-gqhf
CWE: CWE-754
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:L/VI:H/VA:L/SC:L/SI:H/SA:L (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-8x3w-qj7j-gqhf
Type: github-advisory

## Affected
- crates.io: `openmls` — affected >=0 <0.7.2

## Details
Membership and confirmation tags may not be checked correctly due to a missing length check. Any tag that is shorter than the expected tag, but matches up to its length, as well as any empty tag is considered valid.

### Impact

The vulnerability affects a secondary authentication guarantee that MLS provides in certain scenarios. The primary authentication guarantee for all messages comes from the signature on MLS messages. This guarantee is *not* affected by the vulnerability.  
The secondary authentication attests to the group membership of the message author. For MLS private messages, it is implied in the AEAD. For MLS public messages, it is expressed as the ‘membership tag’, a MAC whose key is derived from the private group state only known to group members.

In addition, for public Commit messages, the ‘confirmation tag’ works in a similar manner. Its purpose is to help members who processed the Commit message to ascertain that they now have the same view on the group as the creator of the Commit message for both the private and public group state. 

The vulnerability lets an attacker create MLS messages with a truncated tag that are considered valid nonetheless.

The vulnerability does not affect the primary authentication guarantees of MLS, but breaks post-compromise security (PCS) of the MLS authentication guarantees. As a consequence, an adversary that has compromised a member’s signature key can create valid-looking proposals even after the affected member has successfully updated its key material. However, this is only possible in applications where the following conditions are met:

- The application uses public MLS messages (i.e. it has not restricted the wire format type to private MLS messages only), and  
- the application supports proposals by reference (aka standalone proposals).

Note that, in deployments that allow external Commits, an attacker in possession of a member’s signature key can insert itself into the group without having to forge a membership tag.

### Patches

There are two ways to mitigate the issue:

- Upgrade to openmls v0.7.2: This minor release includes a fix for the issue and bumps the libcrux dependencies. This release does not contain any breaking changes from v0.7.1.  
- Upgrade to openmls v0.8.0: This release contains the fix, as well as other improvements. The list of changes is in [CHANGELOG.md](https://github.com/openmls/openmls/blob/main/CHANGELOG.md). Some of the changes are breaking API changes.

## References
- https://github.com/openmls/openmls/security/advisories/GHSA-8x3w-qj7j-gqhf
- https://github.com/openmls/openmls/commit/91ec049ffc2fa3766110223aa2aabe0303837af8
- https://github.com/openmls/openmls
- https://github.com/openmls/openmls/releases/tag/openmls-v0.7.2
