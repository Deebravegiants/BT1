# [M] c-ares has a use-after-free in read_answers()

## Summary
Severity: Medium
Advisory: CVE-2025-31498
Aliases: GHSA-6hxc-62jh-p29v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2025-04-08
Source: https://osv.dev/vulnerability/CVE-2025-31498
Type: osv

## Details
c-ares is an asynchronous resolver library. From 1.32.3 through 1.34.4, there is a use-after-free in read_answers() when process_answer() may re-enqueue a query either due to a DNS Cookie Failure or when the upstream server does not properly support EDNS, or possibly on TCP queries if the remote closed the connection immediately after a response. If there was an issue trying to put that new transaction on the wire, it would close the connection handle, but read_answers() was still expecting the connection handle to be available to possibly dequeue other responses. In theory a remote attacker might be able to trigger this by flooding the target with ICMP UNREACHABLE packets if they also control the upstream nameserver and can return a result with one of those conditions, this has been untested. Otherwise only a local attacker might be able to change system behavior to make send()/write() return a failure condition. This vulnerability is fixed in 1.34.5.

## References
- http://www.openwall.com/lists/oss-security/2025/04/08/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31498.json
- https://github.com/c-ares/c-ares/security/advisories/GHSA-6hxc-62jh-p29v
- https://nvd.nist.gov/vuln/detail/CVE-2025-31498
- https://github.com/c-ares/c-ares/commit/29d38719112639d8c0ba910254a3dd4f482ea2d1
- https://github.com/c-ares/c-ares/pull/821
