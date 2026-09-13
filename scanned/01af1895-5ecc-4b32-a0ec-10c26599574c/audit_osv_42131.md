# [C] sctp: don't free the ASCONF's own transport in DEL-IP processing

## Summary
Severity: Critical
Advisory: CVE-2026-64564
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-64564
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: don't free the ASCONF's own transport in DEL-IP processing

sctp_process_asconf() caches the transport the ASCONF chunk is processed
against in asconf->transport (== chunk->transport, set once in sctp_rcv()).
For an ASCONF located through its Address Parameter by
__sctp_rcv_asconf_lookup(), that cached transport corresponds to the
Address Parameter, which need not be the packet's source address.

sctp_process_asconf_param() rejects a DEL-IP for the packet source address
(ADDIP D8, SCTP_ERROR_DEL_SRC_IP), but nothing protects asconf->transport.
A single ASCONF can therefore carry, in order:

    [Address Parameter L] [DEL-IP L] [DEL-IP 0.0.0.0]

where L differs from the source. The DEL-IP for L passes the D8 check and
calls sctp_assoc_rm_peer() on the transport that asconf->transport still
points at, freeing it (RCU-deferred). The following wildcard DEL-IP then
reuses the now-dangling asconf->transport in sctp_assoc_set_primary() and
sctp_assoc_del_nonprimary_peers(): set_primary() dereferences the freed
transport (->ipaddr, ->state) and plants the dangling pointer into
asoc->peer.primary_path / active_path, and del_nonprimary_peers(), keeping
only the pointer that is no longer on the list, removes every real
transport, leaving the association with a transport_count of 0 and
primary_path/active_path pointing at freed memory.

Reject a DEL-IP that targets the transport the ASCONF is being processed
against, mirroring the existing source-address guard, so the wildcard
branch can never reuse a freed transport.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/13
- http://www.openwall.com/lists/oss-security/2026/08/06/3
- http://www.openwall.com/lists/oss-security/2026/08/06/4
- http://www.openwall.com/lists/oss-security/2026/08/07/1
- http://www.openwall.com/lists/oss-security/2026/08/07/2
- http://www.openwall.com/lists/oss-security/2026/08/07/8
- https://git.kernel.org/stable/c/2b324ba3494ae958cba16a453e3e71489b4de7fc
- https://git.kernel.org/stable/c/74e8f3e7114f0e26d1b2c4c048044db9fcc27603
- https://git.kernel.org/stable/c/85aca407c560aba81b5ce9d3d6cf94c74077d19b
- https://git.kernel.org/stable/c/9b2854f86f0b56e9027d68e7a3fc909d1a9b566f
- https://git.kernel.org/stable/c/a63afa1f9b12d5293cbe0b77fd45dc0632533a13
- https://git.kernel.org/stable/c/a9ce31be4cb1a5dd82b3e0a1d0c3e7cbdcd31293
- https://git.kernel.org/stable/c/d136b29bf91dd8e3161281b87de597b7311d9462
- https://git.kernel.org/stable/c/fedeb4468987bcaff85fe3061de5ae052d414740
- https://matrix.tencent.com/en/2026/08/06/sctphantom-CVE-2026-64564
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64564.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64564
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
