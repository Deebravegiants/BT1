# [H] CVE-2024-24476

## Summary
Severity: High
Advisory: CVE-2024-24476
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2024-24476
Type: osv

## Details
A buffer overflow in Wireshark before 4.2.0 allows a remote attacker to cause a denial of service via the pan/addr_resolv.c, and ws_manuf_lookup_str(), size components. NOTE: this is disputed by the vendor because neither release 4.2.0 nor any other release was affected.

## References
- https://gist.github.com/1047524396/369ba0ccffe255cf8142208b6142be2b
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZT2BX7UARZVVWKITSZMHW7BHXGIKRSR2/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24476.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZT2BX7UARZVVWKITSZMHW7BHXGIKRSR2/
- https://nvd.nist.gov/vuln/detail/CVE-2024-24476
- https://gitlab.com/wireshark/wireshark/-/issues/19344
- https://github.com/wireshark/wireshark/commit/108217f4bb1afb8b25fc705c2722b3e328b1ad78
