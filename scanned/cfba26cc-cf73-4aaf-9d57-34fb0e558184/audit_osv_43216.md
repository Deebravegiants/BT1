# [C] darknet Integer Overflow in Convolutional Layer Buffer Sizing Leads to Heap Buffer Overflow

## Summary
Severity: Critical
Advisory: CVE-2026-72852
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-72852
Type: osv

## Details
hank-ai/darknet sizes a convolutional layer's weight and output heap buffers by multiplying configuration fields taken from a .cfg file in unchecked 32-bit int arithmetic. In src-lib/convolutional_layer.cpp, l.nweights is computed as (c / groups) * n * size * size and l.outputs as l.out_h * l.out_w * l.out_c, and both feed xcalloc directly. A .cfg whose true dimension product exceeds INT_MAX wraps to a small or zero value, so the allocation is undersized; for example width and height of 256 with filters of 65536 gives 2^32, which wraps to 0. forward_convolutional_layer then re-derives the GEMM dimensions with a different operand order, computing k as l.size*l.size*l.c / l.groups where the allocation divided before multiplying, and reads and writes through the undersized buffer. Loading the crafted .cfg for inference or training is sufficient and no valid .weights file is required. The reported proof of concept observed a heap buffer overflow read in gemm_nn_fast under AddressSanitizer and glibc allocator metadata corruption in a release build of the same input, indicating an out-of-bounds write.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72852.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72852
- https://www.vulncheck.com/advisories/darknet-integer-overflow-in-convolutional-layer-buffer-sizing-leads-to-heap-buffer-overflow
- https://github.com/hank-ai/darknet/issues/148
- https://github.com/hank-ai/darknet
- https://github.com/hank-ai/darknet/blob/v6.0/src-lib/convolutional_layer.cpp#L1457
- https://github.com/hank-ai/darknet/blob/v6.0/src-lib/convolutional_layer.cpp#L764
- https://github.com/hank-ai/darknet/blob/v6.0/src-lib/convolutional_layer.cpp#L811
