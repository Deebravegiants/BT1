# [?] network: avoid panic on invalid fallback DNS resolver (#6654)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2026-06-29
Source: https://github.com/algorand/go-algorand/commit/e39e98059096fae320981932b07c704028cdecde
Type: security-commit

## Details
network: avoid panic on invalid fallback DNS resolver (#6654)

## Patch
### tools/network/resolveController.go
```diff
@@ -62,12 +62,15 @@ func (c *ResolveController) SystemResolver() ResolverIf {
 	return net.DefaultResolver
 }
 
-// FallbackResolver returns a resolver that uses fallback DNS address
+// FallbackResolver returns a resolver that uses the fallback DNS address. If that address
+// cannot be resolved to an IP (e.g. a misconfigured FallbackDNSResolverAddress), it returns
+// the default resolver instead of an unusable one; the non-secure path previously
+// dereferenced a nil *net.IPAddr and panicked.
 func (c *ResolveController) FallbackResolver() ResolverIf {
-	var dnsIPAddr *net.IPAddr
-	var err error
-	if dnsIPAddr, err = net.ResolveIPAddr("ip", c.fallback); err != nil {
-		c.log.Debugf("resolving fallback '%s' failed with %s", c.fallback, err.Error())
+	dnsIPAddr, err := net.ResolveIPAddr("ip", c.fallback)
+	if err != nil || dnsIPAddr == nil {
+		c.log.Warnf("resolving fallback DNS address '%s' failed (%v); using default resolver instead", c.fallback, err)
+		return c.DefaultResolver()
 	}
 
 	if c.secure {
```

### tools/network/resolveController_test.go
```diff
@@ -62,6 +62,28 @@ func TestFallbackResolver(t *testing.T) {
 	a.Equal(r.(*dnssec.Resolver).EffectiveResolverDNS(), []dnssec.ResolverAddress{dnssec.MakeResolverAddress("127.0.0.1", "53")})
 }
 
+func TestFallbackResolverInvalidAddress(t *testing.T) {
+	partitiontest.PartitionTest(t)
+
+	a := require.New(t)
+	log := logging.Base()
+
+	// An unresolvable fallback address (consecutive dots form an empty, syntactically
+	// invalid label, so this fails locally without a network lookup) must degrade to the
+	// default resolver rather than panic on a nil *net.IPAddr.
+	const badAddr = "invalid..fallback..address"
+
+	c := NewResolveController(false, badAddr, log)
+	r := c.FallbackResolver()
+	a.IsType(&Resolver{}, r)
+	a.Equal(defaultDNSAddress, r.(*Resolver).EffectiveResolverDNS())
+
+	c = NewResolveController(true, badAddr, log)
+	r = c.FallbackResolver()
+	a.IsType(&dnssec.Resolver{}, r)
+	a.Equal(dnssec.DefaultDnssecAwareNSServers, r.(*dnssec.Resolver).EffectiveResolverDNS())
+}
+
 func TestDefaultResolver(t *testing.T) {
 	partitiontest.PartitionTest(t)
 
```
