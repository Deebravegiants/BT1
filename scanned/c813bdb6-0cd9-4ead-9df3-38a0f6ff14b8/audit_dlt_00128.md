# [M]  Opened exploitable ports in default docker-compose.yaml 

## Summary
Severity: Medium
Chain: IPFS
Component: ipfs/kubo
Published: 2022-03-21
Source: https://github.com/ipfs/kubo/security/advisories/GHSA-fx5p-f64h-93xc
Type: github-advisory

## Details
### Impact

Allows admin API access to the IPFS node.

### Who ?

This affects people running the  [docker-compose.yaml](https://github.com/ipfs/go-ipfs/blob/master/docker-compose.yaml) service in an environment where the docker host is directly attached to a public or untrusted IP.  In the vulnerable version, the private API endpoint is publicly forwarded by exposing it as `0.0.0.0:5001` on the host machine.  

If the host machine is hidden behind a firewall or NAT (and the LAN is trusted for NAT), this is not an immediate issue because of the protection from the firewall or NAT.  That said, we still recommend users update to follow security best practices of not putting unnecessary dependency on a working firewall.

### Patches
This issue is in [docker-compose.yaml](https://github.com/ipfs/go-ipfs/blob/master/docker-compose.yaml).  Users need to replace their current `docker-compose.yaml` file with a version `0.12.1` or later.

There is no need to update any of the binaries. Users running previous versions like `0.12.0` or earlier can download the `0.12.1` `docker-compose.yaml` file.  You can replace a vulnerable `docker-compose.yaml` file with a the new one with:

```
curl https://raw.githubusercontent.com/ipfs/go-ipfs/v0.12.1/docker-compose.yaml > docker-compose.yaml
```

### How to test if you are vulnerable
#### Binding check on the host
On the host machine, while IPFS is running, run as root:

```bash
netstat -lnp | grep ":5001"
```

The output will be a list of listeners bound to `:5001`.
You then need to check that those listeners are private and preferably even localhost IPs.
⚠️ If this listener is on `0.0.0.0` or a public IP you are very likely vulnerable.

#### Remote hailing
While IPFS is running, you can try to contact the API from a remote machine. (Replace `1.2.3.4` with your node public IP.  Or if you want to test in an untrusted NAT, then substitute the LAN IP instead.)

```bash
curl -X POST http://1.2.3.4:5001/api/v0/version
```


_Trimmed to 38 lines — full report: https://github.com/ipfs/kubo/security/advisories/GHSA-fx5p-f64h-93xc_
