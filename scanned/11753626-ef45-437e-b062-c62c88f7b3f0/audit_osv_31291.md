# [M] NULL pointer dereference in libpcap before 1.10.5 with remote packet capture support

## Summary
Severity: Medium
Advisory: CVE-2024-8006
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-30
Source: https://osv.dev/vulnerability/CVE-2024-8006
Type: osv

## Details
Remote packet capture support is disabled by default in libpcap.  When a user builds libpcap with remote packet capture support enabled, one of the functions that become available is pcap_findalldevs_ex().  One of the function arguments can be a filesystem path, which normally means a directory with input data files.  When the specified path cannot be used as a directory, the function receives NULL from opendir(), but does not check the return value and passes the NULL value to readdir(), which causes a NULL pointer derefence.

## References
- https://github.com/the-tcpdump-group/libpcap/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8006.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8006
- https://github.com/the-tcpdump-group/libpcap/commit/0f8a103469ce87d2b8d68c5130a46ddb7fb5eb29
- https://github.com/the-tcpdump-group/libpcap/commit/8a633ee5b9ecd9d38a587ac9b204e2380713b0d6
