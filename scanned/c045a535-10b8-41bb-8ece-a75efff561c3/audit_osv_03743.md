# [M] ALPINE-CVE-2026-44621

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-44621
Ecosystem: Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-44621
Type: osv

## Affected
- Alpine:v3.24: `unbound` — affected >=0 <1.25.2-r0

## Details
With NLnet Labs Unbound up to and including version 1.25.1, applications using libunbound and configured with 'unwanted-reply-threshold', could eventually be abruptly terminated if the threshold is reached and libunbound needs to call 'libworker_alloc_cleanup' since the function is absent from the function call allow list. When an application using libunbound sets 'unwanted-reply-threshold' to any non-zero value and the iterator queries an authoritative that replies with enough wrong-transaction-ID UDP datagrams to cross the threshold, the 'libworker_alloc_cleanup' will eventually be called. Since the function is absent from the function call allow list, this leads to a fatal exit of libunbound and eventual termination of the embedding application.Unbound itself is not affected since its relevant function 'worker_alloc_cleanup' is registed in the allow list and proceeds to perform the documented cache flush.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-44621
