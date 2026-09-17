# [M] USB: serial: quatech2: fix null-ptr-deref in qt2_process_read_urb()

## Summary
Severity: Medium
Advisory: CVE-2025-21689
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-10
Source: https://osv.dev/vulnerability/CVE-2025-21689
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.178, >=5.16.0 <6.1.128, >=6.2.0 <6.6.75, >=6.7.0 <6.12.12, >=6.13.0 <6.13.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: serial: quatech2: fix null-ptr-deref in qt2_process_read_urb()

This patch addresses a null-ptr-deref in qt2_process_read_urb() due to
an incorrect bounds check in the following:

       if (newport > serial->num_ports) {
               dev_err(&port->dev,
                       "%s - port change to invalid port: %i\n",
                       __func__, newport);
               break;
       }

The condition doesn't account for the valid range of the serial->port
buffer, which is from 0 to serial->num_ports - 1. When newport is equal
to serial->num_ports, the assignment of "port" in the
following code is out-of-bounds and NULL:

       serial_priv->current_port = newport;
       port = serial->port[serial_priv->current_port];

The fix checks if newport is greater than or equal to serial->num_ports
indicating it is out-of-bounds.

## References
- https://git.kernel.org/stable/c/4b9b41fabcd38990f69ef0cee9c631d954a2b530
- https://git.kernel.org/stable/c/575a5adf48b06a2980c9eeffedf699ed5534fade
- https://git.kernel.org/stable/c/6068dcff7f19e9fa6fa23ee03453ad6a40fa4efe
- https://git.kernel.org/stable/c/6377838560c03b36e1153a42ef727533def9b68f
- https://git.kernel.org/stable/c/8542b33622571f54dfc2a267fce378b6e3840b8b
- https://git.kernel.org/stable/c/94770cf7c5124f0268d481886829dc2beecc4507
- https://git.kernel.org/stable/c/f371471708c7d997f763b0e70565026eb67cc470
- https://git.kernel.org/stable/c/fa4c7472469d97c4707698b4c0e098f8cfc2bf22
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21689.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21689
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
