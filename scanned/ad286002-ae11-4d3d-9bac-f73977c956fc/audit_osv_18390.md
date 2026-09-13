# [H] CVE-2020-27173

## Summary
Severity: High
Advisory: CVE-2020-27173
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-16
Source: https://osv.dev/vulnerability/CVE-2020-27173
Type: osv

## Details
In vm-superio before 0.1.1, the serial console FIFO can grow to unlimited memory usage when data is sent to the input source (i.e., standard input). This behavior cannot be reproduced from the guest side. When no rate limiting is in place, the host can be subject to memory pressure, impacting all other VMs running on the same host.

## References
- https://github.com/rust-vmm/vm-superio/issues/17
- https://github.com/rust-vmm/vm-superio/pull/19
