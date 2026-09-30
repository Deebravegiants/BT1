# [M] CVE-2016-6595

## Summary
Severity: Medium
Advisory: CVE-2016-6595
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2016-6595
Type: osv

## Details
The SwarmKit toolkit 1.12.0 for Docker allows remote authenticated users to cause a denial of service (prevention of cluster joins) via a long sequence of join and quit actions.  NOTE: the vendor disputes this issue, stating that this sequence is not "removing the state that is left by old nodes. At some point the manager obviously stops being able to accept new nodes, since it runs out of memory. Given that both for Docker swarm and for Docker Swarmkit nodes are *required* to provide a secret token (it's actually the only mode of operation), this means that no adversary can simply join nodes and exhaust manager resources. We can't do anything about a manager running out of memory and not being able to add new legitimate nodes to the system. This is merely a resource provisioning issue, and definitely not a CVE worthy vulnerability.

## References
- http://www.securityfocus.com/bid/92195
- http://www.securitytracker.com/id/1036548
- http://www.openwall.com/lists/oss-security/2016/08/04/1
- http://www.openwall.com/lists/oss-security/2016/09/02/1
- http://www.openwall.com/lists/oss-security/2016/09/02/8
