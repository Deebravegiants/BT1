# [M] Out-of-bounds read in IPv6 neighbor solicitation in Contiki-NG

## Summary
Severity: Medium
Advisory: CVE-2022-35926
Aliases: GHSA-4hpq-4f53-w386
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-04
Source: https://osv.dev/vulnerability/CVE-2022-35926
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for IoT devices. Because of insufficient validation of IPv6 neighbor discovery options in Contiki-NG, attackers can send neighbor solicitation packets that trigger an out-of-bounds read. The problem exists in the module os/net/ipv6/uip-nd6.c, where memory read operations from the main packet buffer, <code>uip_buf</code>, are not checked if they go out of bounds. In particular, this problem can occur when attempting to read the 2-byte option header and the Source Link-Layer Address Option (SLLAO). This attack requires ipv6 be enabled for the network. The problem has been patched in the develop branch of Contiki-NG. The upcoming 4.8 release of Contiki-NG will include the patch.Users unable to upgrade may apply the patch in Contiki-NG PR #1654.

## References
- https://github.com/contiki-ng/contiki-ng/pull/1654/commits/a4597001d50a04f4b9c78f323ba731e2f979802c
- https://github.com/contiki-ng/contiki-ng/releases/tag/release%2Fv4.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/35xxx/CVE-2022-35926.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-4hpq-4f53-w386
- https://nvd.nist.gov/vuln/detail/CVE-2022-35926
- https://github.com/contiki-ng/contiki-ng/pull/1654
