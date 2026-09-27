# [M] Gitea has insecure default SSH settings

## Summary
Severity: Medium
Advisory: GHSA-3m6q-h5gj-7mrw
CWE: CWE-1188, CWE-327
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-3m6q-h5gj-7mrw
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.0

## Details
## Summary

The built-in SSH server currently advertises a number of key exchange, MAC, and host key algorithms that are considered weak or broken. The defaults should be tightened so a fresh installation passes a baseline SSH security audit out of the box.

## Details

Running `ssh-audit` against a default deployment flags the following as `fail`:

- **Key exchange**
  - `ecdh-sha2-nistp256`
  - `ecdh-sha2-nistp384`
  - `ecdh-sha2-nistp521`
- **MAC**
  - `hmac-sha1`
- **Host key**
  - `ssh-rsa`

## Reproduction

```sh
docker run -it --rm positronsecurity/ssh-audit -p 2222 gitea.local
```

## Impact

Default deployments expose algorithms that are known-weak or deprecated upstream. The current workaround requires manually setting several `GITEA__server__SSH_SERVER_*` variables, which most users will never do.

### Workaround

```ini
[server]
SSH_SERVER_KEY_EXCHANGES = curve25519-sha256, diffie-hellman-group14-sha256
SSH_SERVER_CIPHERS       = chacha20-poly1305@openssh.com, aes128-ctr, aes192-ctr, aes256-ctr, aes128-gcm@openssh.com, aes256-gcm@openssh.com
SSH_SERVER_MACS          = hmac-sha2-256-etm@openssh.com, hmac-sha2-256
```

There is no exposed option to restrict host key algorithms, so `ssh-rsa` remains advertised.

## Acceptance criteria

- [ ] Default `SSH_SERVER_KEY_EXCHANGES`, `SSH_SERVER_CIPHERS`, and `SSH_SERVER_MACS` updated to the secure list above.
- [ ] New `SSH_SERVER_HOST_KEY_ALGORITHMS` option added, with a default that excludes `ssh-rsa`.
- [ ] Documentation updated to reflect the new defaults.
- [ ] `ssh-audit` against a fresh install reports no `[fail]` entries.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-3m6q-h5gj-7mrw
- https://github.com/go-gitea/gitea
