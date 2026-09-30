# [H] PAM module may allow accessing with the credentials of another user

## Summary
Severity: High
Advisory: GHSA-x5q3-c8rm-w787
CVE: CVE-2024-9313
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-x5q3-c8rm-w787
Type: github-advisory

## Affected
- Go: `github.com/ubuntu/authd` — affected >=0 <0.0.0-20240930103526-63e527496b01
- Go: `github.com/ubuntu/authd` — affected >=0.1.0 <0.3.5

## Details
Authd PAM module up to version 0.3.4 can allow broker-managed users to impersonate any other user managed by the same broker and perform any PAM operation with it, including authenticating as them.

This is possible using tools such as `su`, `sudo` or `ssh` (and potentially others) that, so far, do not ensure that the PAM user at the end of the transaction is matching the one who initiated the transaction.

Authd 0.3.5 fixes this by not allowing changing the user unless it was never set before in the PAM stack.

`su` version that will include https://github.com/util-linux/util-linux/pull/3206 will not be affected
`ssh` version that will include https://github.com/openssh/openssh-portable/pull/521 will not be affected
`sudo` version that will include https://github.com/sudo-project/sudo/pull/412 will not be affected
`login` not affected
`passwd` not affected

<details>
<summary>Old report</summary>

### Summary

An user can access as another user using its own credentials

### Details

I feel we’ve a security issue that is due to the fact that we allow changing the user in the cases in which that’s already provided by PAM, I’ve not tested this using the entra-id broker but it’s reproducible with the example one, but unless I’m missing something it should be independent from the broker in use.

Basically, by going to the user selection page we allow to login as any user by entering the use own credentials.

See for example: https://asciinema.org/a/VIcjpDImomaGu0wxsJJxNdmlf or https://asciinema.org/a/CV3D1gaEhn2yclqSMKCnifYPo  

Basically it’s possible to logging in as `user1` using the credentials of `user2` or `user3`.

The issue doesn’t affect login or passwd, but it does affect `su` and `sshd`, since in both cases they don’t check if the `PAM_USER` changed before the final authentication.

Now, while those tools should likely be fixed to only read the PAM_USER once pam gave them the final ok, I think authd should not allow changing the user at all when it has been provided by PAM.
</details>

## References
- https://github.com/ubuntu/authd/security/advisories/GHSA-x5q3-c8rm-w787
- https://nvd.nist.gov/vuln/detail/CVE-2024-9313
- https://github.com/ubuntu/authd/commit/63e527496b013bed46904c1c58be593c13ebdce5
- https://github.com/ubuntu/authd
- https://pkg.go.dev/vuln/GO-2024-3181
- https://www.cve.org/CVERecord?id=CVE-2024-9313
