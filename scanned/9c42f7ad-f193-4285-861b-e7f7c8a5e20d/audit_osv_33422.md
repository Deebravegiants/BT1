# [H] NFSD: Define actions for the new time_deleg FATTR4 attributes

## Summary
Severity: High
Advisory: CVE-2025-40326
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40326
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Define actions for the new time_deleg FATTR4 attributes

NFSv4 clients won't send legitimate GETATTR requests for these new
attributes because they are intended to be used only with CB_GETATTR
and SETATTR. But NFSD has to do something besides crashing if it
ever sees a GETATTR request that queries these attributes.

RFC 8881 Section 18.7.3 states:

> The server MUST return a value for each attribute that the client
> requests if the attribute is supported by the server for the
> target file system. If the server does not support a particular
> attribute on the target file system, then it MUST NOT return the
> attribute value and MUST NOT set the attribute bit in the result
> bitmap. The server MUST return an error if it supports an
> attribute on the target but cannot obtain its value. In that case,
> no attribute values will be returned.

Further, RFC 9754 Section 5 states:

> These new attributes are invalid to be used with GETATTR, VERIFY,
> and NVERIFY, and they can only be used with CB_GETATTR and SETATTR
> by a client holding an appropriate delegation.

Thus there does not appear to be a specific server response mandated
by specification. Taking the guidance that querying these attributes
via GETATTR is "invalid", NFSD will return nfserr_inval, failing the
request entirely.

## References
- https://git.kernel.org/stable/c/4f76435fd517981f01608678c06ad9718a86ee98
- https://git.kernel.org/stable/c/d8f3f94dc950e7c62c96af432c26745885b0a18a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40326.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40326
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
