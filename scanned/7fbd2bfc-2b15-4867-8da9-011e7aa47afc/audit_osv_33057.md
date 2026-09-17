# [H] nvmet: pci-epf: Do not complete commands twice if nvmet_req_init() fails

## Summary
Severity: High
Advisory: CVE-2025-38658
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38658
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet: pci-epf: Do not complete commands twice if nvmet_req_init() fails

Have nvmet_req_init() and req->execute() complete failed commands.

Description of the problem:
nvmet_req_init() calls __nvmet_req_complete() internally upon failure,
e.g., unsupported opcode, which calls the "queue_response" callback,
this results in nvmet_pci_epf_queue_response() being called, which will
call nvmet_pci_epf_complete_iod() if data_len is 0 or if dma_dir is
different from DMA_TO_DEVICE. This results in a double completion as
nvmet_pci_epf_exec_iod_work() also calls nvmet_pci_epf_complete_iod()
when nvmet_req_init() fails.

Steps to reproduce:
On the host send a command with an unsupported opcode with nvme-cli,
For example the admin command "security receive"
$ sudo nvme security-recv /dev/nvme0n1 -n1 -x4096

This triggers a double completion as nvmet_req_init() fails and
nvmet_pci_epf_queue_response() is called, here iod->dma_dir is still
in the default state of "DMA_NONE" as set by default in
nvmet_pci_epf_alloc_iod(), so nvmet_pci_epf_complete_iod() is called.
Because nvmet_req_init() failed nvmet_pci_epf_complete_iod() is also
called in nvmet_pci_epf_exec_iod_work() leading to a double completion.
This not only sends two completions to the host but also corrupts the
state of the PCI NVMe target leading to kernel oops.

This patch lets nvmet_req_init() and req->execute() complete all failed
commands, and removes the double completion case in
nvmet_pci_epf_exec_iod_work() therefore fixing the edge cases where
double completions occurred.

## References
- https://git.kernel.org/stable/c/746d0ac5a07d5da952ef258dd4d75f0b26c96476
- https://git.kernel.org/stable/c/a535c0b10060bc8c174a7964b0f98064ee0c4774
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38658.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38658
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
