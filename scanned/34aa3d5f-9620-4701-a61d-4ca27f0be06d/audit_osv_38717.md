# [H] PackageKit vulnerable to TOCTOU Race on Transaction Flags leads to arbitrary package installation as root

## Summary
Severity: High
Advisory: CVE-2026-41651
Aliases: GHSA-f55j-vvr9-69xv
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41651
Type: osv

## Details
PackageKit is a a D-Bus abstraction layer that allows the user to manage packages in a secure way using a cross-distro, cross-architecture API. PackageKit between and including versions 1.0.2 and 1.3.4 is vulnerable to a time-of-check time-of-use (TOCTOU) race condition on transaction flags that allows unprivileged users to install packages as root and thus leads to a local privilege escalation. This is patched in version 1.3.5.

A local unprivileged user can install arbitrary RPM packages as root, including executing RPM scriptlets, without authentication. The vulnerability is a TOCTOU race condition on `transaction->cached_transaction_flags`  combined with a silent state-machine guard that discards illegal backward transitions while leaving corrupted flags in place. Three bugs exist in `src/pk-transaction.c`:
1. Unconditional flag overwrite (line 4036): `InstallFiles()` writes caller-supplied flags to `transaction->cached_transaction_flags` without checking whether the transaction has already been  authorized/started. A second call blindly overwrites the flags even while the transaction is RUNNING.
2. Silent state-transition rejection (lines 873–882): `pk_transaction_set_state()` silently discards backward state transitions (e.g. `RUNNING` → `WAITING_FOR_AUTH`) but the flag overwrite at step 1 already happened. The transaction continues running with corrupted flags.
3. Late flag read at execution time (lines 2273–2277): The scheduler's idle callback reads cached_transaction_flags at dispatch time, not at authorization time. If flags were overwritten between authorization and execution, the backend sees the attacker's flags.

## References
- http://www.openwall.com/lists/oss-security/2026/04/22/6
- https://github.com/PackageKit/PackageKit/blob/04057883189efa225a7c785591aa87cb299782f8/src/pk-transaction.c#L2273-L2277
- https://github.com/PackageKit/PackageKit/blob/04057883189efa225a7c785591aa87cb299782f8/src/pk-transaction.c#L4036
- https://github.com/PackageKit/PackageKit/blob/04057883189efa225a7c785591aa87cb299782f8/src/pk-transaction.c#L873-L882
- https://github.security.telekom.com/2026/04/pack2theroot-linux-local-privilege-escalation.html
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-41651.json
- https://access.redhat.com/errata/RHSA-2026:11504
- https://access.redhat.com/errata/RHSA-2026:11635
- https://access.redhat.com/errata/RHSA-2026:17558
- https://access.redhat.com/errata/RHSA-2026:17560
- https://access.redhat.com/errata/RHSA-2026:17561
- https://access.redhat.com/errata/RHSA-2026:18024
- https://access.redhat.com/errata/RHSA-2026:18031
- https://access.redhat.com/errata/RHSA-2026:18036
- https://access.redhat.com/errata/RHSA-2026:19141
- https://access.redhat.com/errata/RHSA-2026:19354
- https://access.redhat.com/errata/RHSA-2026:19454
- https://access.redhat.com/errata/RHSA-2026:19601
- https://access.redhat.com/errata/RHSA-2026:22146
- https://access.redhat.com/security/cve/CVE-2026-41651
