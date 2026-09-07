# [H] authd: Primary group ID is incorrectly set to value of UID 

## Summary
Severity: High
Advisory: GHSA-fg3j-5w9g-hmg7
CVE: CVE-2026-6970
CWE: CWE-842
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-fg3j-5w9g-hmg7
Type: github-advisory

## Affected
- Go: `github.com/canonical/authd` — affected >=0.6.0 <0.6.4

## Details
authd 0.6.0 contains [a bug](https://github.com/canonical/authd/issues/1482) which can lead to an incorrect primary group ID.

It affects users whose primary group ID (i.e. the GID in the user record) differs from their UID. There are two ways which can lead to this:

1. The user was created with authd < 0.5.4 (released June 2025). Those users were created with UID != GID.

2. The primary group of the user was modified manually with the authctl utility that is shipped with authd (`authctl group set-gid`).

Another condition is that some user information must have changed in the identity provider (else the user record is not updated upon login). If that is the case, the next time an affected user logs in, authd will set their primary group ID to their UID.

This could lead to local privileges escalation. Also, files and directories created by those users will be owned by that incorrect primary group, which may grant other local users access to those files which they shouldn't have.

Users who are affected by the issue can run this script to fix the primary group ID of all authd users and the file ownership of files in the home directory created with the incorrect GID:

```bash
authd_users=$(getent passwd --service authd | cut -d: -f1)
for user in $authd_users; do
    OLD_GID=$(id -g "$user")
    GID=$(getent group "$user" | cut -d: -f3)
    if [ -z "$GID" ]; then
        echo "Warning: could not determine GID for $user, skipping" >&2
        continue
    fi
    if [ "$OLD_GID" = "$GID" ]; then
        continue  # user not affected
    fi
    USER_HOME=$(getent passwd "$user" | cut -d: -f6)
    echo "Fixing $user: resetting GID from $OLD_GID to $GID"
    sudo authctl group set-gid "$user" "$OLD_GID"
    sudo authctl group set-gid "$user" "$GID"
    sudo chown -R --from=":$OLD_GID" ":$GID" "$USER_HOME"
done
```

After applying the fix, affected users must log out and log back in for `id`, `groups`, and new file GID stamping to reflect the corrected primary group. You may also optionally terminate a user's active session with:

```bash
sudo loginctl terminate-user "$user"
```

If the users also own files outside their home directory, the ownership of those files might have to be updated as well.

Fixed by: https://github.com/canonical/authd/commit/154b428305cb1a7a19c897626fefd09d6dde8b9f

## References
- https://github.com/canonical/authd/security/advisories/GHSA-fg3j-5w9g-hmg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-6970
- https://github.com/canonical/authd/commit/154b428305cb1a7a19c897626fefd09d6dde8b9f
- https://github.com/canonical/authd
