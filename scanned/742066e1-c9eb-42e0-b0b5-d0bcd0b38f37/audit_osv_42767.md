# [M] Iperf3: unbounded peer-controlled allocation in iperf3 json_read() allows unauthenticated remote memory exhaustion

## Summary
Severity: Medium
Advisory: CVE-2026-71218
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-71218
Type: osv

## Details
A flaw was found in iperf3. A remote unauthenticated attacker can exploit a vulnerability in the `JSON_read()` function, which accepts a peer-controlled message length and allocates memory without an upper bound. This allows the attacker to trigger excessive memory consumption, leading to a Denial of Service (DoS) through memory exhaustion, severe slowdown, or termination of the iperf3 service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-71218
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71218.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71218
- https://bugzilla.redhat.com/show_bug.cgi?id=2463003
- https://github.com/esnet/iperf/commit/0128d0357b7e8916fe39e980e455729bc0e5fd4e
