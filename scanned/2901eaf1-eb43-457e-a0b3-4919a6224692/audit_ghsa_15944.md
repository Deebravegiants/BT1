# [M] Authd allows attacker-controlled usernames to yield controllable UIDs

## Summary
Severity: Medium
Advisory: GHSA-4gfw-wf7c-w6g2
CVE: CVE-2024-9312
CWE: CWE-286
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-4gfw-wf7c-w6g2
Type: github-advisory

## Affected
- Go: `github.com/ubuntu/authd` — affected >=0

## Details
CVE description:

Authd, through version 0.3.6, did not sufficiently randomize user IDs to prevent collisions. A local attacker who can register user names could spoof another user's ID and gain their privileges.


----- original report -----
# Cause
authd assigns user IDs as a pure function of the user name. Moreover, the set of UIDs is much too small for pseudo-random assignment to work: the birthday bound predicts random collisions will occur with probability 50% after only 54 562 IDs were assigned.

`authd` only checks for uniqueness [within its local cache](https://github.com/ubuntu/authd/blob/4946962aa4ac6e5b7d2b53503026659581c73907/internal/users/cache/update.go#L67-L71), which
- may be inconsistent across multiple systems within the same domain ;
- may be purged, due to being stored in `/var/cache` ;
- automatically removes entries of users who have not logged into that specific system within the last 6 months.

The current `GenerateID` method, authored in September 2024 (commit a6c85ed24b8d17a2d11c859e8d70f5a52fa69690),
repeatedly hashes the user name until the 4 leading bytes fall into the interval [60 000; 2³¹[ :
https://github.com/ubuntu/authd/blob/f9f851540e6377fca18a45ce7a02d024c1dbd6e9/internal/users/manager.go#L425
https://github.com/ubuntu/authd/blob/f9f851540e6377fca18a45ce7a02d024c1dbd6e9/internal/services/nss/nss.go#L188

Previous versions are affected by similar issues, though without the use of a cryptographic hash in `GenerateID`, making exploitation computationally-easier.


# Impact

Since GenerateID is a pure function with no secret input, and the set of UIDs is small, an adversary which can register users with chosen names can
- register multiple users with colliding IDs, or
- register a single user whose ID collides with a target user's, whether one managed by `authd`, or a system user whose well-known ID is in a range which [overlaps `authd`'s].

In the latter case, as all access control performed by the Linux kernel (and other Unices' kernels) is based on IDs and not usernames, if the attacker can sign into a system, they will have the same privileges as the target user.  The attacker can bypass the uniqueness check in (at least) the following ways:
- engineer a situation where the system administrator purges `/var/cache` ;
- target a system account [whose UID is in `authd`'s range](https://github.com/ubuntu/authd/issues/547) ;
- target an account which hasn't logged into a specific system in more than 6 months.
  Note that this isn't limited to inactive accounts *within the entire domain*, and impersonation on a given system can potentially be leveraged to compromise the target account on other systems; for example:
  - user `alice` is known to log into `1.example.com` ;
  - the attacker computes a preimage (a username which yields the same UID), let's call it `bob` ;
  - the attacker creates the account `bob` and logs into `2.example.com`, succeeding if alice hasn't (recently) logged into that system ;
  - the attacker can now manipulate resources exposed on `2` as if they were alice; assuming `/home` is shared, they could manipulate `~alice/.ssh/authorized_keys`, `~alice/.config`, alice's shell's initialization file, etc.
    Note: NFSv4's `idmap` mechanism may prevent this, but isn't enabled by default (unless Kerberos is used, which isn't the case in an `authd` deployment)
  - at that point, gaining code execution as alice on `1.example.com` is usually trivial.

Since the necessary computation can be performed entirely offline, this wouldn't be affected by any rate-limits, and the only audit trail would be a single user registration. This would require on average less than 2³¹ computations of `GenerateID`: assuming SHA-256's cost is 25 cycles-per-byte, a clock speed of 3GHz, and short (≤32B) generated usernames, this is less than 10 minutes of a single core's time.

[overlaps `authd`'s]: https://github.com/ubuntu/authd/issues/547

# Remediation

The simplest and likely-best remediation path would be for the external IdP to provide a guaranteed-unique user ID in the correct range.
In OIDC, this is commonly communicated through a claim, though its name would need to be configurable as there's no real standard:
- CERN uses `cern_person_id`: https://auth.docs.cern.ch/user-documentation/oidc/config/ ;
- Okta, Zitadel, and many other IdPs, require the realm's administrator to define a custom attribute, conventionally called `uid` or `uidNumber` ;
- etc.

This is also supported by other commonplace identity providers, such as LDAP and Active Directory:
https://learn.microsoft.com/en-us/windows/win32/adschema/a-uidNumber

MS Entra presumably supports this as well.


If that is not possible for some reason, architectural changes to authd would likely be required:
assigning user IDs from a small space (such as Linux's 32b UIDs) requires mutable state to ensure uniqueness, whereas authd's design currently assumes no mutable state is held, aside from some transient, local cache.
Moreover, that mutable state may need to be synchronised across multiple machines as uniform UIDs are often necessary, for instance when accessing a common networked filesystem.


# Acknowledgements

Thanks to Michael Gebetsroither for assisting with the writeup, and Jamie Bliss for the same as well as investigating when the issue was introduced in authd.

## References
- https://github.com/ubuntu/authd/security/advisories/GHSA-4gfw-wf7c-w6g2
- https://nvd.nist.gov/vuln/detail/CVE-2024-9312
- https://github.com/ubuntu/authd
- https://www.cve.org/CVERecord?id=CVE-2024-9312
