# [M] Uninitialized mutex in TLS trusted-credential backend causes kernel NULL-deref DoS under contention

## Summary
Severity: Medium
Advisory: CVE-2026-12233
Aliases: GHSA-57c4-xcq2-fqj7
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-12233
Type: osv

## Details
The PSA Protected Storage credential backend (subsys/net/lib/tls_credentials/tls_credentials_trusted.c) declared its credential-store mutex as a plain zero-filled static struct k_mutex credential_lock; and never called k_mutex_init() on it. A statically zero-filled k_mutex has an uninitialized wait queue (its dlist head/tail are NULL instead of the self-referential sentinels that k_mutex_init/K_MUTEX_DEFINE install). The uncontended lock path does not touch the wait queue, so the defect is latent and serialized use behaves correctly.

When two execution contexts contend on the lock, k_mutex_lock() pends the blocking thread on the wait queue via z_pend_curr(), which calls sys_dlist_append() on the zeroed list and dereferences a NULL tail pointer (tail->next = node), faulting the kernel. The lock is held during TLS handshake credential loading and by all credential add/get/delete operations, so a deployment performing concurrent TLS handshakes (for example a server handling multiple simultaneous connections from a remote peer) or a credential-management operation concurrent with a handshake can trigger the dereference.

The impact is a denial of service: a deterministic kernel panic / device reset on the first contention. There is no memory corruption beyond the NULL dereference and no confidentiality or integrity impact; mutual exclusion on the fast path remains correct. Exposure is limited to builds with CONFIG_TLS_CREDENTIALS_BACKEND_PROTECTED_STORAGE enabled (PSA Protected Storage / TF-M platforms); the default volatile RAM backend initializes its lock correctly and is unaffected.

The fix initializes the mutex statically with K_MUTEX_DEFINE(credential_lock), providing a valid wait queue so the contended path no longer touches a NULL list.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12233.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-57c4-xcq2-fqj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-12233
- https://github.com/zephyrproject-rtos/zephyr/commit/29581d586f3d68ec8bb1448b522e5470d4a06aa9
- https://github.com/zephyrproject-rtos/zephyr
