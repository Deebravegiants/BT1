# [H] libp2p-rust denial of service vulnerability from lack of resource management

## Summary
Severity: High
Advisory: CVE-2022-23486
Aliases: GHSA-jvgw-gccv-q5p8, RUSTSEC-2022-0084
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-07
Source: https://osv.dev/vulnerability/CVE-2022-23486
Type: osv

## Details
libp2p-rust is the official rust language Implementation of the libp2p networking stack. In versions prior to 0.45.1 an attacker node can cause a victim node to allocate a large number of small memory chunks, which can ultimately lead to the victim’s process running out of memory and thus getting killed by its operating system. When executed continuously, this can lead to a denial of service attack, especially relevant on a larger scale when run against more than one node of a libp2p based network. Users are advised to upgrade to `libp2p` `v0.45.1` or above. Users unable to upgrade should reference the DoS Mitigation page for more information on how to incorporate mitigation strategies, monitor their application, and respond to attacks: https://docs.libp2p.io/reference/dos-mitigation/.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23486.json
- https://github.com/libp2p/rust-libp2p/security/advisories/GHSA-jvgw-gccv-q5p8
- https://nvd.nist.gov/vuln/detail/CVE-2022-23486
