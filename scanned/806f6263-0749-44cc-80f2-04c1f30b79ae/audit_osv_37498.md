# [H] crypto: krb5enc - fix async decrypt skipping hash verification

## Summary
Severity: High
Advisory: CVE-2026-31719
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31719
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.25, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: krb5enc - fix async decrypt skipping hash verification

krb5enc_dispatch_decrypt() sets req->base.complete as the skcipher
callback, which is the caller's own completion handler. When the
skcipher completes asynchronously, this signals "done" to the caller
without executing krb5enc_dispatch_decrypt_hash(), completely bypassing
the integrity verification (hash check).

Compare with the encrypt path which correctly uses
krb5enc_encrypt_done as an intermediate callback to chain into the
hash computation on async completion.

Fix by adding krb5enc_decrypt_done as an intermediate callback that
chains into krb5enc_dispatch_decrypt_hash() upon async skcipher
completion, matching the encrypt path's callback pattern.

Also fix EBUSY/EINPROGRESS handling throughout: remove
krb5enc_request_complete() which incorrectly swallowed EINPROGRESS
notifications that must be passed up to callers waiting on backlogged
requests, and add missing EBUSY checks in krb5enc_encrypt_ahash_done
for the dispatch_encrypt return value.


Unset MAY_BACKLOG on the async completion path so the user won't
see back-to-back EINPROGRESS notifications.

## References
- https://git.kernel.org/stable/c/07cbb1bd424370671814a862913c99a6e1441588
- https://git.kernel.org/stable/c/3bfbf5f0a99c991769ec562721285df7ab69240b
- https://git.kernel.org/stable/c/e51f42114abbdf47f29dda43e7826be28907fcd2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31719.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31719
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
