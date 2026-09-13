# [H] BIT-node-2024-21892

## Summary
Severity: High
Advisory: BIT-node-2024-21892
Aliases: BIT-node-min-2024-21892, CVE-2024-21892
Ecosystem: Bitnami
Published: 2024-05-24
Source: https://osv.dev/vulnerability/BIT-node-2024-21892
Type: osv

## Affected
- Bitnami: `node` — affected >=21.0.0 <21.6.2

## Details
On Linux, Node.js ignores certain environment variables if those may have been set by an unprivileged user while the process is running with elevated privileges with the only exception of CAP_NET_BIND_SERVICE.
Due to a bug in the implementation of this exception, Node.js incorrectly applies this exception even when certain other capabilities have been set.
This allows unprivileged users to inject code that inherits the process's elevated privileges.

## References
- http://www.openwall.com/lists/oss-security/2024/03/11/1
- https://hackerone.com/reports/2237545
- https://security.netapp.com/advisory/ntap-20240322-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2024-21892
- https://bugzilla.redhat.com/show_bug.cgi?id=2264582
- https://github.com/nodejs/node/commit/10ecf400679e04eddab940721cad3f6c1d603b61
- https://github.com/nodejs/node/commit/2a5a150772c6a41795314340c8697035a1b344b6
- https://github.com/nodejs/node/commit/b43171c6f669b2223064343e2c8472582586f727
- https://github.com/nodejs/node/commit/e6b4c105e0795fba8afb3f8e910c56ba9e60f4b5
- https://www.oracle.com/security-alerts/cpuapr2024.html
