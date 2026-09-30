# [M] CVE-2021-46985

## Summary
Severity: Medium
Advisory: CVE-2021-46985
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46985
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPI: scan: Fix a memory leak in an error handling path

If 'acpi_device_set_name()' fails, we must free
'acpi_device_bus_id->bus_id' or there is a (potential) memory leak.

## References
- https://git.kernel.org/stable/c/5ab9857dde7c3ea3faef6b128d718cf8ba98721b
- https://git.kernel.org/stable/c/6901a4f795e0e8d65ae779cb37fc22e0bf294712
- https://git.kernel.org/stable/c/69cc821e89ce572884548ac54c4f80eec7a837a5
- https://git.kernel.org/stable/c/a7e17a8d421ae23c920240625b4413c7b94d94a4
- https://git.kernel.org/stable/c/c5c8f6ffc942cf42f990f22e35bcf4cbe9d8c2fb
- https://git.kernel.org/stable/c/dafd4c0b5e835db020cff11c74b4af9493a58e72
- https://git.kernel.org/stable/c/e2381174daeae0ca35eddffef02dcc8de8c1ef8a
- https://git.kernel.org/stable/c/0c8bd174f0fc131bc9dfab35cd8784f59045da87
