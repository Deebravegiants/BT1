# [M] NeuVector has an insecure password storage and is vulnerable to rainbow attack

## Summary
Severity: Medium
Advisory: GHSA-8ff6-pc43-jwv3
CVE: CVE-2025-53884
CWE: CWE-759, CWE-916
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-8ff6-pc43-jwv3
Type: github-advisory

## Affected
- Go: `github.com/neuvector/neuvector` — affected >=0 <0.0.0-20250825191744-da1a462074c3

## Details
### Impact

NeuVector stores user passwords and API keys using a simple, unsalted hash. This method is vulnerable to rainbow table attack (offline attack where hashes of known passwords are precomputed).

NeuVector generates a cryptographically secure, random 16-character salt and uses it with the PBKDF2 algorithm to create the hash value for the following actions:

- Creating a user
- Updating a user’s password
- Creating an API key

**Note:** After upgrading to NeuVector 5.4.6, users must log in again so that NeuVector can regenerate the password hash. For API keys, you must send at least one request per API key to regenerate its hash value.

### Patches

This issue is fixed in NeuVector version **5.4.6** and later.

### Workarounds

There is no workaround. Upgrade to a patched version of NeuVector as soon as possible.

### References

If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [NeuVector](https://github.com/neuvector/neuvector/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-neuvector/support-matrix/all-supported-versions/neuvector-v-all-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/#suse-security).

## References
- https://github.com/neuvector/neuvector/security/advisories/GHSA-8ff6-pc43-jwv3
- https://nvd.nist.gov/vuln/detail/CVE-2025-53884
- https://github.com/neuvector/neuvector/pull/2084
- https://github.com/neuvector/neuvector/pull/2085
- https://github.com/neuvector/neuvector/commit/addc9308b3a6359c9789a62ac6e73594c9a544d0
- https://github.com/neuvector/neuvector/commit/da1a462074c3d7d426dba0901840fd0e2146f63a
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-53884
- https://github.com/neuvector/neuvector
