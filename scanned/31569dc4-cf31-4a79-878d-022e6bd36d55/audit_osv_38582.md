# [H] CVE-2026-40622

## Summary
Severity: High
Advisory: CVE-2026-40622
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-40622
Type: osv

## Details
NLnet Labs Unbound 1.16.2 up to and including version 1.25.0 has a vulnerability of the 'ghost domain names' family of attacks that could extend the ghost domain window by up to one cached TTL configured value. Similar to other 'ghost domain names' attacks, an adversary needs to control a (ghost) zone and be able to query a vulnerable Unbound. A single client NS query can cause Unbound to overwrite the cached expired parent-side referral NS rrset with the child-side apex NS rrset and essentially extend the ghost domain window by up to one cached TTL configured value ('cache-max-ttl'). In configurations where 'harden-referral-path: yes' is used (non-default configuration), no client NS query is required since Unbound implicitly performs that query. Unbound 1.25.1 contains a patch with a fix that does not allow extension of TTLs for (parent) NS records regardless of their trust.

## References
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2026-40622.txt
