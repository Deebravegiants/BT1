# [M] Import of incorrectly embargoed keys could cause early publication

## Summary
Severity: Medium
Advisory: GHSA-3wxm-m9m4-cprj
Ecosystem: Go
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-3wxm-m9m4-cprj
Type: github-advisory

## Affected
- Go: `github.com/google/exposure-notifications-server` — affected >=0 <0.18.3
- Go: `github.com/google/exposure-notifications-server` — affected >=0.19.0 <0.19.2

## Details
### Impact

If your installation is using the `export-importer` service, there is potential impact.
If your installation is not importing keys via the `export-importer` services, your installation is not impacted.

In versions `0.19.1` and earlier, the `export-importer` service assumed that the server it was importing from had properly embargoed keys for at least 2 hours after their expiry time. There are now known instances of servers that did not properly embargo keys.

This could allow allow for imported keys to be re-published before they have expired, allowing for potential replay of RPIs.

### Patches

This is patched in `v0.18.3` and all versions `0.19.2` and later.

### Workarounds

Ensure that the servers you are importing export zip files from are not publishing keys too early. 

### References

n/a

### For more information

If you have any questions or comments about this advisory
* Open an issue in [exposure-notifications-server](https://github.com/google/exposure-notifications-server/)
* Email us at [exposure-notifications-feedback@google.com](mailto:exposure-notifications-feedback@google.com)

## References
- https://github.com/google/exposure-notifications-server/security/advisories/GHSA-3wxm-m9m4-cprj
