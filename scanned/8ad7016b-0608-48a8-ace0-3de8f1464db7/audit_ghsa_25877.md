# [H] Gogs vulnerable to improper PAM authorization handling

## Summary
Severity: High
Advisory: GHSA-gw5h-h6hj-f56g
CVE: CVE-2022-0871
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-03-14
Source: https://github.com/advisories/GHSA-gw5h-h6hj-f56g
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.5

## Details
### Impact

Expired PAM accounts and accounts with expired passwords are continued to be seen as valid. Installations use PAM as authentication sources are affected.

### Patches

Expired PAM accounts and accounts with expired passwords are no longer being seen as valid. Users should upgrade to 0.12.5 or the latest 0.13.0+dev.

### Workarounds

In addition to marking PAM accounts as expired, also disable/lock them. Running `usermod -L <username>` will add an exclamation mark to the password hash and would result in wrong passwords responses when trying to login. 

### References

https://huntr.dev/bounties/ea82cfc9-b55c-41fe-ae58-0d0e0bd7ab62/

### For more information

If you have any questions or comments about this advisory, please post on https://github.com/gogs/gogs/issues/6810.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-gw5h-h6hj-f56g
- https://nvd.nist.gov/vuln/detail/CVE-2022-0871
- https://github.com/gogs/gogs/issues/6810
- https://github.com/gogs/gogs/commit/64102be2c90e1b47dbdd379873ba76c80d4b0e78
- https://github.com/gogs/gogs
- https://huntr.dev/bounties/ea82cfc9-b55c-41fe-ae58-0d0e0bd7ab62
