# [M] CVE-2026-42923

## Summary
Severity: Medium
Advisory: CVE-2026-42923
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-42923
Type: osv

## Details
NLnet Labs Unbound up to and including version 1.25.0 has a vulnerability in the DNSSEC validator where the code path to consult the negative cache for DS records does not take into account the limit on NSEC3 hash calculations introduced in 1.19.1. This leads to degradation of service during the attack. An adversary that controls a DNSSEC signed zone can exploit this by signing NSEC3 records with acceptably high iterations for child delegations and querying a vulnerable Unbound. Unbound will keep performing the allowed hash calculations on the NSEC3 records and will not limit the work by the mitigation introduced in 1.19.1. As a side effect, a global lock for the negative cache will be held for the duration of the hashing, blocking other threads that need to consult the negative cache. Coordinated attacks could raise the vulnerability to denial of service. Unbound 1.25.1 contains a patch with a fix to bound the vulnerable code path with the existing limit for NSEC3 hash calculations.

## References
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2026-42923.txt
