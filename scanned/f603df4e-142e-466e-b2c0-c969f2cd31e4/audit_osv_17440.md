# [C] CVE-2020-15173

## Summary
Severity: Critical
Advisory: CVE-2020-15173
Aliases: GHSA-rr68-fchr-69vf
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-09
Source: https://osv.dev/vulnerability/CVE-2020-15173
Type: osv

## Details
In ACCEL-PPP (an implementation of PPTP/PPPoE/L2TP/SSTP), there is a buffer overflow when receiving an l2tp control packet ith an AVP which type is a string and no hidden flags, length set to less than 6. If your application is used in open networks or there are untrusted nodes in the network it is highly recommended to apply the patch. The problem was patched with commit 2324bcd5ba12cf28f47357a8f03cd41b7c04c52b As a workaround changes of commit 2324bcd5ba12cf28f47357a8f03cd41b7c04c52b can be applied to older versions.

## References
- https://github.com/accel-ppp/accel-ppp/security/advisories/GHSA-rr68-fchr-69vf
- https://github.com/accel-ppp/accel-ppp/commit/2324bcd5ba12cf28f47357a8f03cd41b7c04c52b
