# [M] Silver has unrestricted traffic between Wireguard clients

## Summary
Severity: Medium
Advisory: GHSA-q8j9-34qf-7vq7
CVE: CVE-2025-27093
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-q8j9-34qf-7vq7
Type: github-advisory

## Affected
- Go: `github.com/BishopFox/sliver` — affected >=0 <1.5.44
- Go: `github.com/bishopfox/sliver` — affected >=0 <1.5.44

## Details
### Summary
Sliver's custom Wireguard netstack doesn't limit traffic between Wireguard clients, this could lead to:
1. Leaked/recovered keypair (from a beacon) being used to attack operators.
2. Port forwardings usable from other implants.


### Details
1. Sliver treat operators' Wireguard config and beacon/session's Wireguard config equally, they both connect to the wireguard listener created from the CLI.

2. The current netstack implementation does not filter traffic between clients. 
I think this piece of code handle traffic between clients, from experimental results clients can ping and connect to each other freely, and I didn't see any filtering here either:
```
File: server\c2\wireguard.go
246: func socketWGWriteEnvelope(connection net.Conn, envelope *sliverpb.Envelope) error {
247: 	data, err := proto.Marshal(envelope)
248: 	if err != nil {
249: 		wgLog.Errorf("Envelope marshaling error: %v", err)
250: 		return err
251: 	}
252: 	dataLengthBuf := new(bytes.Buffer)
253: 	binary.Write(dataLengthBuf, binary.LittleEndian, uint32(len(data)))
254: 	connection.Write(dataLengthBuf.Bytes())
255: 	connection.Write(data)
256: 	return nil
257: }
258: 

```
3. The docs says to use a Wireguard clients and operator wg-config to connect to the same WG listener as beacons:
https://sliver.sh/docs?name=Port%20Forwarding

4. If the operator uses official wireguard clients that integrates with the OS's netstack (I'm using the [Windows client](https://www.wireguard.com/install/)) then their services are accessible on the wireguard interface's IP address (for example 100.64.0.3) when the services listen on 0.0.0.0 (SSH, RDP, SMB, etc) 
![image](https://github.com/user-attachments/assets/8c791655-6f77-423c-8274-389e0850436b)

5. The beacon's wireguard private key can be recovered through a process dump or other forensic techniques.
6. When a private key is recovered, an attacker can connect to 100.64.0.1:1337 (key exchange listener) to generate new wireguard clients without the operators' knowledge, in that way achieve persistence inside the wireguard network.


### PoC
Easy way:
1. Create 2 operators wireguard config.
2. Connect them both to the wireguard listener.
3. From one machine, ping/scan/connect to the other's services like RDP (3389), SSH (22), etc.

Slightly complicated way:
1. From the operator's machine, connect to the wireguard listener.
2. On the attacker's machine, run a beacon.
3. Dump the process
4. Find the private key, public key, endpoint, etc in the dump file:
![image](https://github.com/user-attachments/assets/84d3841f-398d-4bca-939f-bf8ed2881be7)
![image](https://github.com/user-attachments/assets/000c7d02-b6f0-4b12-82e5-29eddfff93f8)
![image](https://github.com/user-attachments/assets/3d0a3e80-3a16-4434-8622-1832c5865a85)
![image](https://github.com/user-attachments/assets/a17f73ab-622b-4852-9c15-0ad5c5afa0eb)

5. Construct a valid Wireguard config based on the strings found. On the attacker's machine, connect to the Wireguard listener.
6. Ping/scan/connect to the other's services like RDP (3389), SSH (22), etc.

### Impact
The operator's machine is impacted, if their services contain a vulnerability, an attacker can exploit it and gain RCE. If not then it could be used to gather information (Hostname, SSH signature, etc).

### Suggestion
1. Filter traffic between clients with a default-deny policy.
2. Differentiate between operators and beacons' wireguard config/client
3. Only allow specific one-way traffic when the operator request to open a Wireguard port forward.

### Vulnerable versions
All versions containing wireguard functionality.

## References
- https://github.com/BishopFox/sliver/security/advisories/GHSA-q8j9-34qf-7vq7
- https://nvd.nist.gov/vuln/detail/CVE-2025-27093
- https://github.com/BishopFox/sliver/commit/8e5c5f14506d6d60ebb3362e6b9857ab1e0d76ff
- https://github.com/BishopFox/sliver/commit/9122878cbbcae543eb8210f616550382af2065fd
- https://github.com/BishopFox/sliver
- https://pkg.go.dev/vuln/GO-2025-4079
