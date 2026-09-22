# [H] ARP unbounded memory usage

## Summary
Severity: High
Advisory: OSEC-2026-02
Ecosystem: opam
CVSS: 7.4 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/OSEC-2026-02
Type: osv

## Affected
- opam: `arp` — affected >=0 <4.1.0, >=0 <a700d9f139a387839172dde816660472023cb13f

## Details
## Background

Mirage's implementation of the ARP protocol (RFC826) caches ARP replies to construct an IPv4 address -> MAC address cache. This cache is long-lived (effectively global), and also contains pending ARP requests, which are replaced by the reply, or deleted after a timeout. ARP replies that do not match any entry in the ARP cache are ignored (dropped).

The maximum amount of memory that a Solo5 unikernel can be assigned is 4GiB (see X86_GUEST_MAX_SIZE and AARCH64_MMIO_BASE).

## Problem description

There are no no size constraints on the cache, and with 2^32 IPv4 addresses, it can exceed the maximum amount of memory that can be allocated by a unikernel if an attacker has Layer-2 access to that unikernel and can spoof arbitrary IP addresses. An attacker also needs to trick the unikernel into sending out an ARP query (ARP replies that don't have a corresponding Pending or Dynamic entry in the ARP table are ignored), this can be done by spoofing an ICMP echo request for example. However while attempting to develop an exploit for this another vulnerability was discovered (reported separately).

## Impact

All versions of 'arp' are affected, and this module is typically used by a unikernel that provides network services. An affected unikernel can crash with an Out of memory condition. Unikernels that do not have network devices are not affected.

## Workaround

Devices on the same network/bridge as a unikernel should have firewall rules (on their TAP devices) that prevent sending ARP packets with IPv4 addresses that the unikernel doesn't own (although this becomes difficult to enforce if DHCP is used).

Unikernel orchestrators can be configured to restart unikernels on crash, although you'd still lose any state that was in memory.

## Solution

Use a cache with a fixed upper bound on size, e.g. a LRU cache that drops old entries.

## Timeline

2025-05-23: issue discovered by Edwin Török while reviewing code to debug another OOM crash as part of the HACKSAT25 challenge
2025-05-28: issue reported to security@mirage.io
2025-10-20: arp 4.1.0 was released
2026-02-18: security advisory was published

## References
- https://github.com/mirage/arp/pull/35
