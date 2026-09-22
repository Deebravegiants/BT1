# [H] Input: synaptics-rmi4 - zero report size on F54 work error

## Summary
Severity: High
Advisory: CVE-2026-80570
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80570
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: synaptics-rmi4 - zero report size on F54 work error

In rmi_f54_work(), if an error occurs during report request or command
verification, the code jumped directly to the 'error' label, bypassing
the 'abort' label where f54->report_size was normally zeroed out.

This left f54->report_size containing its previous successful payload
size. If a user then altered the V4L2 format to a smaller size, and a
subsequent run failed, rmi_f54_buffer_queue() would copy the stale,
larger payload size into the shrunken V4L2 buffer, causing a heap
buffer overflow.

Fix this by merging the 'abort' and 'error' labels into a single 'out'
exit path, and ensuring that f54->report_size is always set to 0 on
failure by checking for error and zeroing the local report_size first.

## References
- https://git.kernel.org/stable/c/62079c17ec07d64362bec367ee7a525b0dbf6bf9
- https://git.kernel.org/stable/c/77749685e55da19b187df215b5da4080842ca5c7
- https://git.kernel.org/stable/c/79521ed3cc9ea48476666ccacf45ecd6954b29a4
- https://git.kernel.org/stable/c/88c8174d72900d77fbdf2f527d54b6ff2da876a8
- https://git.kernel.org/stable/c/b28593a05afdd812b590e1045b5bd862a5869225
- https://git.kernel.org/stable/c/c669c64ab71afa7b467c4d7e18f6a05e96b97a1f
- https://git.kernel.org/stable/c/c6cfda79f26c69e97db9805808c3b44d02227b4b
- https://git.kernel.org/stable/c/dc76c3c8e8ad09362b8c1561f3928288c15cba2e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80570.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80570
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
