# [M] CVE-2021-47620

## Summary
Severity: Medium
Advisory: CVE-2021-47620
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2021-47620
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: refactor malicious adv data check

Check for out-of-bound read was being performed at the end of while
num_reports loop, and would fill journal with false positives. Added
check to beginning of loop processing so that it doesn't get checked
after ptr has been advanced.

## References
- https://git.kernel.org/stable/c/899663be5e75dc0174dc8bda0b5e6826edf0b29a
- https://git.kernel.org/stable/c/bcea886771c3f22a590c8c8b9139a107bd7f1e1c
- https://git.kernel.org/stable/c/5c968affa804ba98c3c603f37ffea6fba618025e
- https://git.kernel.org/stable/c/835d3706852537bf92eb23eb8635b8dee0c0aa67
- https://git.kernel.org/stable/c/83d5196b65d1b29e27d7dd16a3b9b439fb1d2dba
- https://git.kernel.org/stable/c/8819f93cd4a443dfe547aa622b21f723757df3fb
- https://git.kernel.org/stable/c/305e92f525450f3e1b5f5c9dc7eadb152d66a082
- https://git.kernel.org/stable/c/5a539c08d743d9910631448da78af5e961664c0e
- https://git.kernel.org/stable/c/7889b38a7f21ed19314f83194622b195d328465c
