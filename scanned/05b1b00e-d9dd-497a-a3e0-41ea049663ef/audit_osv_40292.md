# [H] ksmbd: scope conn->binding slowpath to bound sessions only

## Summary
Severity: High
Advisory: CVE-2026-52911
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2026-52911
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: scope conn->binding slowpath to bound sessions only

When the binding SESSION_SETUP sets conn->binding = true, the flag stays
set after the call so that the global session lookup in
ksmbd_session_lookup_all() can find the session, which was not added to
conn->sessions. Because the flag is connection-wide, the global lookup
path will also resolve any other session by id if asked.

Tighten the global lookup so that the returned session must have this
connection registered in its channel xarray (sess->ksmbd_chann_list).
The channel entry is installed by the existing binding_session path in
ntlm_authenticate()/krb5_authenticate() when a SESSION_SETUP completes
successfully, so this condition is a strict equivalent of "this
connection has been accepted as a channel of this session". Connections
that have not bound to a given session cannot reach it via the global
table.

The existing conn->binding gate for entering the slowpath is preserved
so that non-binding connections keep the fast-path-only behavior, and
the session->state check is unchanged.

## References
- https://git.kernel.org/stable/c/1e2bec062c5c9ec282636715166056d0998d746d
- https://git.kernel.org/stable/c/1ff46c9915c1cbf454db58a8cb87f7cac818e6a6
- https://git.kernel.org/stable/c/2cc8a4db633b10715450b291c1343859a4b2c509
- https://git.kernel.org/stable/c/974c1c224e85549dc3459f3bb2255bbbdd2b9372
- https://git.kernel.org/stable/c/b0da97c034b6107d14e537e212d4ce8b22109a58
- https://git.kernel.org/stable/c/e3a93ce6e25757b8f375e38b8f91e1d9da4edc1a
- https://git.kernel.org/stable/c/e74c00c6af428a39e564cdc5bd3a3648c6d8de87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52911.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52911
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
