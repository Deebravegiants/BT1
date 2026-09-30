# [?] Fix a race condition during initialization (#11444) (#11698)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2022-11-29
Source: https://github.com/OffchainLabs/prysm/commit/e49d8f2162159244b408e0fab8fd4c33ce91ca5f
Type: security-commit

## Details
Fix a race condition during initialization (#11444) (#11698)

* Fix a race condition during initialization (#11444)

* Fix tests

* Add more test cases

Co-authored-by: Preston Van Loon <preston@prysmaticlabs.com>
Co-authored-by: james-prysm <90280386+james-prysm@users.noreply.github.com>
Co-authored-by: Raul Jordan <raul@prysmaticlabs.com>

## Patch
### beacon-chain/p2p/connection_gater.go
```diff
@@ -41,6 +41,10 @@ func (s *Service) InterceptAddrDial(pid peer.ID, m multiaddr.Multiaddr) (allow b
 
 // InterceptAccept checks whether the incidental inbound connection is allowed.
 func (s *Service) InterceptAccept(n network.ConnMultiaddrs) (allow bool) {
+	// Deny all incoming connections before we are ready
+	if !s.started {
+		return false
+	}
 	if !s.validateDial(n.RemoteMultiaddr()) {
 		// Allow other go-routines to run in the event
 		// we receive a large amount of junk connections.
```

### beacon-chain/p2p/connection_gater_test.go
```diff
@@ -40,6 +40,7 @@ func TestPeer_AtMaxLimit(t *testing.T) {
 	s.cfg = &Config{MaxPeers: 0}
 	s.addrFilter, err = configureFilter(&Config{})
 	require.NoError(t, err)
+	s.started = true
 	h1, err := libp2p.New([]libp2p.Option{privKeyOption(pkey), libp2p.ListenAddrs(listen), libp2p.ConnectionGater(s)}...)
 	require.NoError(t, err)
 	s.host = h1
@@ -83,6 +84,7 @@ func TestService_InterceptBannedIP(t *testing.T) {
 	ip := "212.67.10.122"
 	multiAddress, err := ma.NewMultiaddr(fmt.Sprintf("/ip4/%s/tcp/%d", ip, 3000))
 	require.NoError(t, err)
+	s.started = true
 
 	for i := 0; i < ipBurst; i++ {
 		valid := s.validateDial(multiAddress)
@@ -96,6 +98,37 @@ func TestService_InterceptBannedIP(t *testing.T) {
 	}
 }
 
+func TestService_RejectInboundConnectionBeforeStarted(t *testing.T) {
+	limit := 1
+	s := &Service{
+		ipLimiter: leakybucket.NewCollector(ipLimit, ipBurst, 1*time.Second, false),
+		peers: peers.NewStatus(context.Background(), &peers.StatusConfig{
+			PeerLimit:    limit,
+			ScorerParams: &scorers.Config{},
+		}),
+		host: mockp2p.NewTestP2P(t).BHost,
+		cfg:  &Config{MaxPeers: uint(limit)},
+	}
+	var err error
+	s.addrFilter, err = configureFilter(&Config{})
+	require.NoError(t, err)
+
+	ip := "212.67.10.122"
+	multiAddress, err := ma.NewMultiaddr(fmt.Sprintf("/ip4/%s/tcp/%d", ip, 3000))
+	require.NoError(t, err)
+
+	valid := s.InterceptAccept(&maEndpoints{raddr: multiAddress})
+	if valid {
+		t.Errorf("Expected multiaddress with ip %s to be rejected as p2p service is not ready", ip)
+	}
+
+	s.started = true
+	valid = s.InterceptAccept(&maEndpoints{raddr: multiAddress})
+	if !valid {
+		t.Errorf("Expected multiaddress with ip %s to be accepted after service is started", ip)
+	}
+}
+
 func TestService_RejectInboundPeersBeyondLimit(t *testing.T) {
 	limit := 20
 	s := &Service{
@@ -113,6 +146,7 @@ func TestService_RejectInboundPeersBeyondLimit(t *testing.T) {
 	ip := "212.67.10.122"
 	multiAddress, err := ma.NewMultiaddr(fmt.Sprintf("/ip4/%s/tcp/%d", ip, 3000))
 	require.NoError(t, err)
+	s.started = true
 
 	valid := s.InterceptAccept(&maEndpoints{raddr: multiAddress})
 	if !valid {
@@ -157,6 +191,7 @@ func TestPeer_BelowMaxLimit(t *testing.T) {
 	h1, err := libp2p.New([]libp2p.Option{privKeyOption(pkey), libp2p.ListenAddrs(listen), libp2p.ConnectionGater(s)}...)
 	require.NoError(t, err)
 	s.host = h1
+	s.started = true
 	defer func() {
 		err := h1.Close()
 		require.NoError(t, err)
@@ -202,6 +237,7 @@ func TestPeerAllowList(t *testing.T) {
 	h1, err := libp2p.New([]libp2p.Option{privKeyOption(pkey), libp2p.ListenAddrs(listen), libp2p.ConnectionGater(s)}...)
 	require.NoError(t, err)
 	s.host = h1
+	s.started = true
 	defer func() {
 		err := h1.Close()
 		require.NoError(t, err)
@@ -248,6 +284,7 @@ func TestPeerDenyList(t *testing.T) {
 	h1, err := libp2p.New([]libp2p.Option{privKeyOption(pkey), libp2p.ListenAddrs(listen), libp2p.ConnectionGater(s)}...)
 	require.NoError(t, err)
 	s.host = h1
+	s.started = true
 	defer func() {
 		err := h1.Close()
 		require.NoError(t, err)
```
