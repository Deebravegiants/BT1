# [?] Update openssl for CVE-2022-0778 (#3095)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2022-03-17
Source: https://github.com/sigp/lighthouse/commit/a1befd89aaae8bf45d99ddf9cfb4834175069dd4
Type: security-commit

## Details
Update openssl for CVE-2022-0778 (#3095)

## Issue Addressed

Fix the `cargo-audit` failure for the recent openssl bug involving parsing of untrusted certificates (CVE-2022-0778).

## Additional Info

Lighthouse loads remote certificates in the following cases:

* When connecting to an eth1 node (`--eth1-endpoints`).
* When connecting to a beacon node from the VC (`--beacon-nodes`).
* When connecting to a beacon node for checkpoint sync (`--checkpoint-sync-url`).

In all of these cases we are already placing a lot of trust in the server at the other end, however due to the scope for MITM attacks we are still potentially vulnerable. E.g. an ISP could inject an invalid certificate for the remote host which would cause Lighthouse to hang indefinitely.
