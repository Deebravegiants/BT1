# [M] Remote packet capture support is disabled by default in libpcap

## Summary
Severity: Medium
Advisory: JLSEC-2026-765
Ecosystem: Julia
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/JLSEC-2026-765
Type: osv

## Affected
- Julia: `libpcap_jll` — affected >=0 <1.10.5+0

## Details
Remote packet capture support is disabled by default in libpcap.  When a user builds libpcap with remote packet capture support enabled, one of the functions that become available is `pcap_findalldevs_ex()`.  One of the function arguments can be a filesystem path, which normally means a directory with input data files.  When the specified path cannot be used as a directory, the function receives NULL from opendir(), but does not check the return value and passes the NULL value to readdir(), which causes a NULL pointer derefence.

## References
- https://github.com/advisories/GHSA-gj9v-677h-mwcx
- https://github.com/the-tcpdump-group/libpcap/commit/0f8a103469ce87d2b8d68c5130a46ddb7fb5eb29
- https://github.com/the-tcpdump-group/libpcap/commit/8a633ee5b9ecd9d38a587ac9b204e2380713b0d6
- https://nvd.nist.gov/vuln/detail/CVE-2024-8006
