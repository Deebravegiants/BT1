# [?] Merge pull request #10914 from erickcestari/fix-panic-discovery

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2026-06-24
Source: https://github.com/lightningnetwork/lnd/commit/c6768ca4ff104ab228bebe7b4264385fb0bd32ee
Type: security-commit

## Details
Merge pull request #10914 from erickcestari/fix-panic-discovery

discovery: fix panic in DNS fallback SRV lookup

## Patch
### discovery/bootstrapper.go
```diff
@@ -382,13 +382,19 @@ func (d *DNSSeedBootstrapper) fallBackSRVLookup(soaShim string,
 		return nil, err
 	}
 
+	if len(addrs) == 0 {
+		return nil, fmt.Errorf("no addresses for fallback DNS seed "+
+			"shim %v", soaShim)
+	}
+
 	// Once we have the IP address, we'll establish a TCP connection using
 	// port 53.
 	dnsServer := net.JoinHostPort(addrs[0], "53")
 	conn, err := d.net.Dial("tcp", dnsServer, d.timeout)
 	if err != nil {
 		return nil, err
 	}
+	_ = conn.SetDeadline(time.Now().Add(d.timeout))
 
 	dnsHost := fmt.Sprintf("_nodes._tcp.%v.", targetEndPoint)
 	dnsConn := &dns.Conn{Conn: conn}
@@ -416,7 +422,18 @@ func (d *DNSSeedBootstrapper) fallBackSRVLookup(soaShim string,
 	// that net.LookupSRV would normally return.
 	var rrs []*net.SRV
 	for _, rr := range resp.Answer {
-		srv := rr.(*dns.SRV)
+		// The answer section may contain records other than SRV
+		// (e.g. A or CNAME), so use the comma-ok form to skip any
+		// non-SRV record instead of panicking on a failed type
+		// assertion.
+		srv, ok := rr.(*dns.SRV)
+		if !ok {
+			log.Infof("Skipping non-SRV record %T in fallback "+
+				"DNS seed response for %v", rr, targetEndPoint)
+
+			continue
+		}
+
 		rrs = append(rrs, &net.SRV{
 			Target:   srv.Target,
 			Port:     srv.Port,
@@ -425,6 +442,11 @@ func (d *DNSSeedBootstrapper) fallBackSRVLookup(soaShim string,
 		})
 	}
 
+	if len(rrs) == 0 {
+		return nil, fmt.Errorf("no SRV records in fallback DNS seed "+
+			"response for %v", targetEndPoint)
+	}
+
 	return rrs, nil
 }
 
@@ -498,7 +520,9 @@ search:
 			bechNodeHost := nodeSrv.Target
 			addrs, err := d.net.LookupHost(bechNodeHost)
 			if err != nil {
-				return nil, err
+				log.Tracef("Skipping node %v: %v",
+					bechNodeHost, err)
+				continue
 			}
 
 			if len(addrs) == 0 {
@@ -523,7 +547,9 @@ search:
 			bechNode := strings.Split(bechNodeHost, ".")
 			_, nodeBytes5Bits, err := bech32.Decode(bechNode[0])
 			if err != nil {
-				return nil, err
+				log.Tracef("Skipping node %v: %v",
+					bechNodeHost, err)
+				continue
 			}
 
 			// Once we have the bech32 decoded pubkey, we'll need
@@ -534,11 +560,15 @@ search:
 				nodeBytes5Bits, 5, 8, false,
 			)
 			if err != nil {
-				return nil, err
+				log.Tracef("Skipping node %v: %v",
+					bechNodeHost, err)
+				continue
 			}
 			nodeKey, err := btcec.ParsePubKey(nodeBytes)
 			if err != nil {
-				return nil, err
+				log.Tracef("Skipping node %v: %v",
+					bechNodeHost, err)
+				continue
 			}
 
 			// If we have an ignore list, and this node is in the
```

### discovery/bootstrapper_test.go
```diff
@@ -2,12 +2,15 @@ package discovery
 
 import (
 	"context"
+	"fmt"
 	"net"
 	"testing"
+	"time"
 
 	"github.com/btcsuite/btcd/btcec/v2"
 	"github.com/lightningnetwork/lnd/autopilot"
 	"github.com/lightningnetwork/lnd/tor"
+	"github.com/miekg/dns"
 	"github.com/stretchr/testify/require"
 )
 
@@ -55,6 +58,60 @@ func (s *stubChannelGraph) ForEachNodesChannels(_ context.Context,
 	return nil
 }
 
+// fallbackNet is a tor.Net stub used to drive fallBackSRVLookup. LookupHost
+// returns shimAddrs and Dial serves a single DNS response, written by
+// serveResp, over an in-memory pipe so the fallback path can be exercised
+// without a real DNS server.
+type fallbackNet struct {
+	shimAddrs []string
+	serveResp func(question *dns.Msg) *dns.Msg
+}
+
+// Dial returns one end of an in-memory pipe and spins up a goroutine acting as
+// the DNS server on the other end, which reads the SRV query and writes back
+// the response produced by serveResp.
+func (n *fallbackNet) Dial(_, _ string,
+	_ time.Duration) (net.Conn, error) {
+
+	client, server := net.Pipe()
+
+	// Act as the DNS server on the far end of the pipe: read the SRV
+	// query, then write back the crafted response.
+	go func() {
+		srvConn := &dns.Conn{Conn: server}
+		defer srvConn.Close()
+
+		query, err := srvConn.ReadMsg()
+		if err != nil {
+			return
+		}
+
+		_ = srvConn.WriteMsg(n.serveResp(query))
+	}()
+
+	return client, nil
+}
+
+// LookupHost returns the configured shim addresses used to reach the fallback
+// DNS server.
+func (n *fallbackNet) LookupHost(_ string) ([]string, error) {
+	return n.shimAddrs, nil
+}
+
+// LookupSRV is unsupported by this stub; the fallback path under test issues
+// the SRV query manually over the Dial connection instead.
+func (n *fallbackNet) LookupSRV(_, _, _ string,
+	_ time.Duration) (string, []*net.SRV, error) {
+
+	return "", nil, fmt.Errorf("unsupported")
+}
+
+// ResolveTCPAddr is unsupported by this stub as it is not exercised by the
+// fallback SRV lookup path.
+func (n *fallbackNet) ResolveTCPAddr(_, _ string) (*net.TCPAddr, error) {
+	return nil, fmt.Errorf("unsupported")
+}
+
 // TestGraphBootstrapperSkipsV2Onion ensures SampleNodeAddrs strips Tor v2
 // .onion entries from the returned candidate set so the connection manager
 // never attempts to dial an obsolete v2 hidden service surfaced through the
@@ -145,3 +202,163 @@ func TestGraphBootstrapperSkipsV2Onion(t *testing.T) {
 			"v2-only node %x should contribute nothing", s.pub)
 	}
 }
+
+// TestFallBackSRVLookupSkipsNonSRV ensures a DNS response whose Answer section
+// contains non-SRV records (which an on-path attacker or malicious seed can
+// inject, since the response is unauthenticated) is filtered rather than
+// triggering a type-assertion panic that would crash the daemon.
+func TestFallBackSRVLookupSkipsNonSRV(t *testing.T) {
+	t.Parallel()
+
+	const target = "nodes.lightning.directory"
+
+	srvTarget := "ln1qexample._nodes._tcp." + target + "."
+
+	netStub := &fallbackNet{
+		shimAddrs: []string{"127.0.0.1"},
+		serveResp: func(q *dns.Msg) *dns.Msg {
+			resp := new(dns.Msg)
+			resp.SetReply(q)
+			resp.Rcode = dns.RcodeSuccess
+
+			// A hostile/malformed Answer section: an A record and a
+			// CNAME interleaved with a single valid SRV record.
+			resp.Answer = []dns.RR{
+				&dns.A{
+					Hdr: dns.RR_Header{
+						Name:   q.Question[0].Name,
+						Rrtype: dns.TypeA,
+					},
+					A: net.ParseIP("1.2.3.4"),
+				},
+				&dns.CNAME{
+					Hdr: dns.RR_Header{
+						Name:   q.Question[0].Name,
+						Rrtype: dns.TypeCNAME,
+					},
+					Target: "evil.example.",
+				},
+				&dns.SRV{
+					Hdr: dns.RR_Header{
+						Name:   q.Question[0].Name,
+						Rrtype: dns.TypeSRV,
+					},
+					Target: srvTarget,
+					Port:   9735,
+				},
+			}
+
+			return resp
+		},
+	}
+
+	bs := NewDNSSeedBootstrapper(
+		[][2]string{{target, "soa.lightning.directory"}},
+		netStub, time.Second,
+	)
+	d, ok := bs.(*DNSSeedBootstrapper)
+	require.True(t, ok)
+
+	// The non-SRV records must be skipped, leaving only the valid SRV
+	// record. Crucially, this must not panic.
+	srvs, err := d.fallBackSRVLookup("soa.lightning.directory", target)
+	require.NoError(t, err)
+	require.Len(t, srvs, 1)
+	require.Equal(t, srvTarget, srvs[0].Target)
+}
+
+// TestFallBackSRVLookupNoSRVRecords ensures a successful DNS response whose
+// Answer section holds no SRV records (only CNAME/A entries, or is empty)
+// returns an error rather than (nil, nil), so the caller does not mistake "no
+// usable records" for a successful query.
+func TestFallBackSRVLookupNoSRVRecords(t *testing.T) {
+	t.Parallel()
+
+	const target = "nodes.lightning.directory"
+
+	netStub := &fallbackNet{
+		shimAddrs: []string{"127.0.0.1"},
+		serveResp: func(q *dns.Msg) *dns.Msg {
+			resp := new(dns.Msg)
+			resp.SetReply(q)
+			resp.Rcode = dns.RcodeSuccess
+
+			// Only a non-SRV record is present in the Answer
+			// section, leaving zero usable SRV targets.
+			resp.Answer = []dns.RR{
+				&dns.A{
+					Hdr: dns.RR_Header{
+						Name:   q.Question[0].Name,
+						Rrtype: dns.TypeA,
+					},
+					A: net.ParseIP("1.2.3.4"),
+				},
+			}
+
+			return resp
+		},
+	}
+
+	bs := NewDNSSeedBootstrapper(
+		[][2]string{{target, "soa.lightning.directory"}},
+		netStub, time.Second,
+	)
+	d, ok := bs.(*DNSSeedBootstrapper)
+	require.True(t, ok)
+
+	srvs, err := d.fallBackSRVLookup("soa.lightning.directory", target)
+	require.Error(t, err)
+	require.Empty(t, srvs)
+}
+
+// TestFallBackSRVLookupEmptyAnswer ensures a successful DNS response with an
+// entirely empty Answer section returns an error rather than (nil, nil), so the
+// caller does not mistake an empty response for a successful query.
+func TestFallBackSRVLookupEmptyAnswer(t *testing.T) {
+	t.Parallel()
+
+	const target = "nodes.lightning.directory"
+
+	netStub := &fallbackNet{
+		shimAddrs: []string{"127.0.0.1"},
+		serveResp: func(q *dns.Msg) *dns.Msg {
+			resp := new(dns.Msg)
+			resp.SetReply(q)
+			resp.Rcode = dns.RcodeSuccess
+
+			// Leave the Answer section empty.
+			resp.Answer = nil
+
+			return resp
+		},
+	}
+
+	bs := NewDNSSeedBootstrapper(
+		[][2]string{{target, "soa.lightning.directory"}},
+		netStub, time.Second,
+	)
+	d, ok := bs.(*DNSSeedBootstrapper)
+	require.True(t, ok)
+
+	srvs, err := d.fallBackSRVLookup("soa.lightning.directory", target)
+	require.Error(t, err)
+	require.Empty(t, srvs)
+}
+
+// TestFallBackSRVLookupNoShimAddrs ensures an empty LookupHost result for the
+// fallback shim returns an error instead of panicking on an out-of-bounds
+// index.
+func TestFallBackSRVLookupNoShimAddrs(t *testing.T) {
+	t.Parallel()
+
+	netStub := &fallbackNet{shimAddrs: nil}
+
+	bs := NewDNSSeedBootstrapper(nil, netStub, time.Second)
+	d, ok := bs.(*DNSSeedBootstrapper)
+	require.True(t, ok)
+
+	_, err := d.fallBackSRVLookup(
+		"soa.lightning.directory", "nodes.lightning.directory",
+	)
+	require.Error(t, err)
+}
```

### docs/release-notes/release-notes-0.22.0.md
```diff
@@ -42,6 +42,12 @@
   regardless of peer connectivity. Uptime is now seeded from the peer's
   actual connection state.
 
+* [Fixed a panic](https://github.com/lightningnetwork/lnd/pull/10914) in the
+  DNS fallback SRV lookup, which unconditionally type-asserted each DNS Answer
+  record to `*dns.SRV` and crashed the daemon when the response contained a
+  non-SRV record. Non-SRV records are now skipped, and an empty `LookupHost`
+  result for the shim no longer triggers an out-of-bounds index.
+
 # New Features
 
 ## Functional Enhancements
```
