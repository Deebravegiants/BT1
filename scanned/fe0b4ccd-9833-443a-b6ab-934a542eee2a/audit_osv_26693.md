# [H] cifs: fix mid leak during reconnection after timeout threshold

## Summary
Severity: High
Advisory: CVE-2023-53597
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53597
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.150, >=5.16.0 <6.1.42, >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: fix mid leak during reconnection after timeout threshold

When the number of responses with status of STATUS_IO_TIMEOUT
exceeds a specified threshold (NUM_STATUS_IO_TIMEOUT), we reconnect
the connection. But we do not return the mid, or the credits
returned for the mid, or reduce the number of in-flight requests.

This bug could result in the server->in_flight count to go bad,
and also cause a leak in the mids.

This change moves the check to a few lines below where the
response is decrypted, even of the response is read from the
transform header. This way, the code for returning the mids
can be reused.

Also, the cifs_reconnect was reconnecting just the transport
connection before. In case of multi-channel, this may not be
what we want to do after several timeouts. Changed that to
reconnect the session and the tree too.

Also renamed NUM_STATUS_IO_TIMEOUT to a more appropriate name
MAX_STATUS_IO_TIMEOUT.

## References
- https://git.kernel.org/stable/c/57d25e9905c71133e201f6d06b56a3403d4ad433
- https://git.kernel.org/stable/c/69cba9d3c1284e0838ae408830a02c4a063104bc
- https://git.kernel.org/stable/c/c55901d381a22300c9922170e59704059f50977b
- https://git.kernel.org/stable/c/df31d05f0678cdd0796ea19983a2b93edca18bb0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53597.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53597
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
