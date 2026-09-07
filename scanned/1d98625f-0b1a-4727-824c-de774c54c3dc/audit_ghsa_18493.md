# [M] Moby firewalld reload makes published container ports accessible from remote hosts 

## Summary
Severity: Medium
Advisory: GHSA-x4rx-4gw3-53p4
CVE: CVE-2025-54388
CWE: CWE-909
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-29
Source: https://github.com/advisories/GHSA-x4rx-4gw3-53p4
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=28.2.0 <28.3.3

## Details
Moby is an open source container framework developed by Docker Inc. that is distributed as Docker Engine, Mirantis Container Runtime, and various other downstream projects/products. The Moby daemon component (dockerd), which is developed as [moby/moby](https://github.com/moby/moby) is commonly referred to as Docker, or Docker Engine.

Firewalld is a daemon used by some Linux distributions to provide a dynamically managed firewall. When Firewalld is running, Docker uses its iptables backend to create rules, including rules to isolate containers in one bridge network from containers in other bridge networks.

### Impact

The iptables rules created by Docker are removed when firewalld is reloaded using, for example "firewall-cmd --reload", "killall -HUP firewalld", or "systemctl reload firewalld".

When that happens, Docker must re-create the rules. However, in affected versions of Docker, the iptables rules that prevent packets arriving on a host interface from reaching container addresses are not re-created.

Once these rules have been removed, a remote host configured with a route to a Docker bridge network can access published ports, even when those ports were only published to a loopback address. Unpublished ports remain inaccessible.

For example, following a firewalld reload on a Docker host with address `192.168.0.10` and a bridge network with subnet `172.17.0.0/16`, running the following command on another host in the local network will give it access to published ports on container addresses in that network: `ip route add 172.17.0.0/16 via 192.168.0.10`.

Containers running in networks created with `--internal` or equivalent have no access to other networks. Containers that are only connected to these networks remain isolated after a firewalld reload.

Where Docker Engine is not running in the host's network namespace, it is unaffected. Including, for example, Rootless Mode, and Docker Desktop.

### Patches

Moby releases older than 28.2.0 are not affected. A fix is available in moby release 28.3.3.

### Workarounds
After reloading firewalld, either:
- Restart the docker daemon,
- Re-create bridge networks, or
- Use rootless mode.

### References
https://firewalld.org/
https://firewalld.org/documentation/howto/reload-firewalld.html

## References
- https://github.com/moby/moby/security/advisories/GHSA-x4rx-4gw3-53p4
- https://nvd.nist.gov/vuln/detail/CVE-2025-54388
- https://github.com/moby/moby/pull/50506
- https://github.com/moby/moby/commit/bea959c7b793b32a893820b97c4eadc7c87fabb0
- https://github.com/moby/moby
