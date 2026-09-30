# [?] p2p/net/dial: fixed data race

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2015-01-24
Source: https://github.com/libp2p/go-libp2p/commit/ffc7eac22d920d015bb1b437ad1399ec25e5e490
Type: security-commit

## Details
p2p/net/dial: fixed data race

## Patch
### net/conn/dial.go
```diff
@@ -89,10 +89,17 @@ func (d *Dialer) rawConnDial(ctx context.Context, raddr ma.Multiaddr, remote pee
 	laddr := pickLocalAddr(d.LocalAddrs, raddr)
 	log.Debugf("%s dialing %s -- %s --> %s", d.LocalPeer, remote, laddr, raddr)
 
+	// make a copy of the manet.Dialer, we may need to change its timeout.
+	madialer := d.Dialer
+
 	if laddr != nil && reuseport.Available() {
+		// we're perhaps going to dial twice. half the timeout, so we can afford to.
+		// otherwise our context would expire right after the first dial.
+		madialer.Dialer.Timeout = (madialer.Dialer.Timeout / 2)
+
 		// dial using reuseport.Dialer, because we're probably reusing addrs.
 		// this is optimistic, as the reuseDial may fail to bind the port.
-		if nconn, retry, reuseErr := d.reuseDial(laddr, raddr); reuseErr == nil {
+		if nconn, retry, reuseErr := reuseDial(madialer.Dialer, laddr, raddr); reuseErr == nil {
 			// if it worked, wrap the raw net.Conn with our manet.Conn
 			log.Debugf("%s reuse worked! %s %s %s", d.LocalPeer, laddr, nconn.RemoteAddr(), nconn)
 			return manet.WrapNetConn(nconn)
@@ -105,22 +112,18 @@ func (d *Dialer) rawConnDial(ctx context.Context, raddr ma.Multiaddr, remote pee
 		}
 	}
 
-	// no local addr, or reuseport failed. just dial straight with a new port.
-	return d.Dialer.Dial(raddr)
+	return madialer.Dial(raddr)
 }
 
-func (d *Dialer) reuseDial(laddr, raddr ma.Multiaddr) (conn net.Conn, retry bool, err error) {
+func reuseDial(dialer net.Dialer, laddr, raddr ma.Multiaddr) (conn net.Conn, retry bool, err error) {
 	if laddr == nil {
 		// if we're given no local address no sense in using reuseport to dial, dial out as usual.
 		return nil, true, reuseport.ErrReuseFailed
 	}
 
-	// half the timeout so we can retry regularly if this fails.
-	d.Dialer.Dialer.Timeout = (d.Dialer.Dialer.Timeout / 2)
-
 	// give reuse.Dialer the manet.Dialer's Dialer.
 	// (wow, Dialer should've so been an interface...)
-	rd := reuseport.Dialer{d.Dialer.Dialer}
+	rd := reuseport.Dialer{dialer}
 
 	// get the local net.Addr manually
 	rd.D.LocalAddr, err = manet.ToNetAddr(laddr)
```
