# [M] darknet through 6.0 Out-of-Bounds Read and Write via Unchecked Layer Index in .cfg Parser

## Summary
Severity: Medium
Advisory: CVE-2026-81334
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81334
Type: osv

## Details
darknet subscripts its layer array with an index taken from a configuration file without checking it against the array's length. The array is allocated in src-lib/darknet_network.cpp as xcalloc(net.n, sizeof(Darknet::Layer)), sized to exactly the number of layer sections the file declares. The shortcut, scale_channels and sam sections supply that index through their from field and the route section through its layers field, and parse_shortcut_section in src-lib/darknet_cfg.cpp reads net.layers[index].outputs with no bounds check, which reads past the allocation. The dispatch loop in create_network then reuses the same index to assign net.layers[l.index].use_bin_output and net.layers[l.index].keep_delta_gpu, writing past the allocation at an offset the file controls, with a fixed one-byte value. Parsing a crafted configuration file is sufficient: the parse runs before any weights file is opened and needs no non-default option, so the result is a reliable crash and a write whose location, though not its value, is chosen by whoever supplied the file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81334.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81334
- https://www.vulncheck.com/advisories/darknet-through-6.0-out-of-bounds-read-and-write-via-unchecked-layer-index-in-cfg-parser
- https://github.com/hank-ai/darknet
- https://github.com/hank-ai/darknet/blob/v6.0/src-lib/darknet_cfg.cpp
- https://github.com/hank-ai/darknet/blob/v6.0/src-lib/darknet_network.cpp
