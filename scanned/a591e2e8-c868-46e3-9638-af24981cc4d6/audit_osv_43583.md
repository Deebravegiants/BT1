# [H] afs: handle CB.InitCallBackState3 requests without a server record

## Summary
Severity: High
Advisory: CVE-2026-74425
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74425
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: handle CB.InitCallBackState3 requests without a server record

The cache manager callback path now attaches the server record to an
incoming call through the rxrpc peer's app data.  That association is
not guaranteed to exist for every callback request, and most callback
handlers already tolerate that case.

Make CB.InitCallBackState3 follow the same pattern by checking whether a
server record was attached before using it.  If the peer is not mapped
to a server record, trace the request and ignore it, matching the
existing behaviour for other unmatched callback requests.

This keeps the callback handler consistent with the rest of the cache
manager service and avoids depending on peer state that may not be
available for a given request.

## References
- https://git.kernel.org/stable/c/0bd5f2786a878148190b4c7c259d01313d5f2357
- https://git.kernel.org/stable/c/42e3917cdbdc3d35e191c525687a6d5427f237fd
- https://git.kernel.org/stable/c/cc848a080f7a6848dfeef441722419fdcbfe9b8d
- https://git.kernel.org/stable/c/f3cf725cd284b7912d5522babb44721bf38c8887
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74425.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74425
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
