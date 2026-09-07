# [M] IPv6 enabled on IPv4-only network interfaces

## Summary
Severity: Medium
Advisory: GHSA-x84c-p2g9-rqv9
CVE: CVE-2024-32473
CWE: CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-18
Source: https://github.com/advisories/GHSA-x84c-p2g9-rqv9
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=26.0.0 <26.0.2

## Details
In 26.0.0 and 26.0.1, IPv6 is not disabled on network interfaces, including those belonging to networks where `--ipv6=false`.

### Impact

A container with an `ipvlan` or `macvlan` interface will normally be configured to share an external network link with the host machine. Because of this direct access, with IPv6 enabled:

- Containers may be able to communicate with other hosts on the local network over link-local IPv6 addresses.
- If router advertisements are being broadcast over the local network, containers may get SLAAC-assigned addresses.
- The interface  will be a member of IPv6 multicast groups.

This means interfaces in IPv4-only networks present an unexpectedly and unnecessarily increased attack surface.

A container with an unexpected IPv6 address can do anything a container configured with an IPv6 address can do. That is, listen for connections on its IPv6 address, open connections to other nodes on the network over IPv6, or attempt a DoS attack by flooding packets from its IPv6 address. This has CVSS score AV:L/AC:H/PR:N/UI:R/S:C/C:N/I:N/A:L (2.7).

Because the container may not be constrained by an IPv6 firewall, there is increased potential for data exfiltration from the container. This has CVSS score AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (4.7).

A remote attacker could send malicious Router Advertisements to divert traffic to itself, a black-hole, or another device. The same attack is possible today for IPv4 macvlan/ipvlan endpoints with ARP spoofing, TLS is commonly used by Internet APIs to mitigate this risk. The presence of an IPv6 route could impact the container's availability by indirectly abusing the behaviour of software which behaves poorly in a dual-stack environment. For example, it could resolve a name to a DNS AAAA record and keep trying to connect over IPv6 without ever falling back to IPv4, potentially denying service to the container. This has CVSS score AV:A/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (4.5).

### Patches

The issue is patched in 26.0.2.

### Workarounds

To completely disable IPv6 in a container, use `--sysctl=net.ipv6.conf.all.disable_ipv6=1` in the `docker create` or `docker run` command. Or, in the service configuration of a `compose` file, the equivalent:

```
        sysctls:
            - net.ipv6.conf.all.disable_ipv6=1
```

### References

- sysctl configuration using `docker run`:
  - https://docs.docker.com/reference/cli/docker/container/run/#sysctl
- sysctl configuration using `docker compose`:
  - https://docs.docker.com/compose/compose-file/compose-file-v3/#sysctls

## References
- https://github.com/moby/moby/security/advisories/GHSA-x84c-p2g9-rqv9
- https://nvd.nist.gov/vuln/detail/CVE-2024-32473
- https://github.com/moby/moby/commit/7cef0d9cd1cf221d8c0b7b7aeda69552649e0642
- https://github.com/moby/moby
