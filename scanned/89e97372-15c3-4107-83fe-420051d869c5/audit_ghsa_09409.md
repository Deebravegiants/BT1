# [H] SimpleSAMLphp casserver FileSystemTicketStore path traversal allows out-of-ticket-directory read/unserialize and conditional deletion

## Summary
Severity: High
Advisory: GHSA-jrrg-99xh-5j2q
CVE: CVE-2026-46491
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-jrrg-99xh-5j2q
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp-module-casserver` — affected >=0 <7.0.3

## Details
## Summary

`simplesamlphp-module-casserver` builds file paths for the file-based CAS ticket store by directly concatenating the configured ticket directory with an attacker-controlled ticket identifier. Public CAS validation/proxy endpoints pass attacker-controlled `ticket` / `pgt` query parameters into this store.

In deployments using `FileSystemTicketStore`, a remote attacker can use path traversal sequences such as `../target.serialized` to make the CAS server read and unserialize files outside the ticket directory. In the CAS 1.0 validation flow, the same attacker-selected path is also passed to `deleteTicket()` immediately after `getTicket()` returns, which can delete the target file when it is readable by the PHP process, deletable under the PHP process filesystem permissions, and unserializes to a value compatible with the `?array` return type.

### Preconditions

The demonstrated issue requires:

- the `casserver` module to be enabled;
- the file-based ticket store to be configured (`FileSystemTicketStore`);
- public CAS validation/proxy endpoints to be reachable;
- the PHP process to have filesystem permissions for the target path.
- for the demonstrated CAS 1.0 deletion impact, `getTicket()` must return without throwing; practically, the target file must contain serialized PHP data that unserializes to a value compatible with the `?array` return type, such as an array or null. Full CAS semantic validation is not required for deletion in CAS 1.0 because `deleteTicket($ticket)` is called immediately after `getTicket($ticket)`.

The attacker does not need administrator access to SimpleSAMLphp.

## Impact

Affected deployments can allow remote attackers to escape the configured CAS ticket directory through public ticket validation inputs.

Confirmed impact:

- read and unserialize files outside the ticket cache when the file content is valid serialized PHP data;
- delete attacker-selected files outside the ticket cache through the CAS 1.0 validation flow when the target is readable by the PHP process, deletable under the PHP process filesystem permissions, and the target content unserializes to a value compatible with the `?array` return type, such as a serialized array or serialized null. Full CAS semantic validation is not required before deletion in the CAS 1.0 flow.

The file deletion impact depends on filesystem permissions of the PHP process. In realistic deployments, this can destroy CAS tickets, serialized SimpleSAMLphp runtime/cache files, or other writable files whose contents can be unserialized into a value accepted by the `?array` return type. It may also delete attacker-created files outside the ticket directory if the attacker has another primitive to place such serialized content.

The `unserialize()` call creates a dangerous secondary primitive if an attacker can place a serialized object file at a reachable path, although this report does not claim a complete object-injection or RCE chain.

## References
- https://github.com/simplesamlphp/simplesamlphp-module-casserver/security/advisories/GHSA-jrrg-99xh-5j2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-46491
- https://github.com/simplesamlphp/simplesamlphp-module-casserver/commit/b84f3e4ed57c4d97e0dc73df102e7eff831a681f
- https://github.com/simplesamlphp/simplesamlphp-module-casserver
- https://github.com/simplesamlphp/simplesamlphp-module-casserver/releases/tag/v7.0.3
