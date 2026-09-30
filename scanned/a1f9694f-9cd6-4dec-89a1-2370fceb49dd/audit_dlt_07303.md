# [?] testing: fix data race accessing messagesOfInterest during network shutdown (#2181)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-05-26
Source: https://github.com/algorand/go-algorand/commit/4e763c8560f6edf019796578639e895b7d2cef99
Type: security-commit

## Details
testing: fix data race accessing messagesOfInterest during network shutdown (#2181)

<!--
Thanks for submitting a pull request! We appreciate the time and effort you spent to get this far.

If you haven't already, please make sure that you've reviewed the CONTRIBUTING guide:
https://github.com/algorand/go-algorand/blob/master/CONTRIBUTING.md#code-guidelines

In particular ensure that you've run the following:
* make generate
* make sanity (which runs make fmt, make lint, make fix and make vet)

It is also a good idea to run tests:
* make test
* make integration
-->

## Summary

Fix race [reported here](https://github.com/algorand/go-algorand-internal/issues/1268):
```
Read at 0x00c00675ed48 by goroutine 210:
  github.com/algorand/go-algorand/network.(*WebsocketNetwork).ServeHTTP()
      /home/travis/gopath/src/github.com/algorand/go-algorand/network/wsNetwork.go:1114 +0x19ad
  github.com/gorilla/mux.(*Router).ServeHTTP()
      /home/travis/gopath/pkg/mod/github.com/gorilla/mux@v1.6.2/mux.go:162 +0x193
  github.com/algorand/go-algorand/network.(*RequestTracker).ServeHTTP()
      /home/travis/gopath/src/github.com/algorand/go-algorand/network/requestTracker.go:474 +0x77b
  net/http.serverHandler.ServeHTTP()
      /home/travis/.gimme/versions/go1.14.7.linux.amd64/src/net/http/server.go:2836 +0xce
  net/http.(*conn).serve()
      /home/travis/.gimme/versions/go1.14.7.linux.amd64/src/net/http/server.go:1924 +0x837
Previous write at 0x00c00675ed48 by goroutine 79:
  github.com/algorand/go-algorand/network.(*WebsocketNetwork).Stop()
      /home/travis/gopath/src/github.com/algorand/go-algorand/network/wsNetwork.go:855 +0x265
  github.com/algorand/go-algorand/network.TestGetPeers()
      /home/travis/gopath/src/github.com/algorand/go-algorand/network/wsNetwork_test.go:977 +0xe1d
  testing.tRunner()
      /home/travis/.gimme/versions/go1.14.7.linux.amd64/src/testing/testing.go:1039 +0x1eb

```

## Test Plan

The CI should run this test. I don't think the flaky test runs on pull requests right now, but it should run during the nightly builds. 

The race is not reproducible on my system. Running this before and after the test does not report any errors (until a 10 minute timeout):
```
$ gotestsum --format testname -- -tags "sqlite_unlock_notify sqlite_omit_load_extension osusergo netgo static_build" -race github.com/algorand/go-algorand/network -run TestGetPeers -count 1000000000
```

## Patch
### network/requestTracker.go
```diff
@@ -379,6 +379,29 @@ func (rt *RequestTracker) Close() error {
 	return rt.listener.Close()
 }
 
+func (rt *RequestTracker) getWaitUntilNoConnectionsChannel(checkInterval time.Duration) <-chan struct{}{
+	done := make(chan struct{})
+
+	go func() {
+		checkEmpty := func (rt *RequestTracker) bool {
+			rt.httpConnectionsMu.Lock()
+			defer rt.httpConnectionsMu.Unlock()
+			return len(rt.httpConnections) == 0
+		}
+
+		for true {
+			if checkEmpty(rt) {
+				close(done)
+				return
+			}
+
+			time.Sleep(checkInterval)
+		}
+	}()
+
+	return done
+}
+
 // Addr returns the listener's network address.
 func (rt *RequestTracker) Addr() net.Addr {
 	return rt.listener.Addr()
```

### network/wsNetwork.go
```diff
@@ -849,8 +849,11 @@ func (wn *WebsocketNetwork) Stop() {
 		wn.log.Debugf("closed %s", listenAddr)
 	}
 
+	// Wait for the requestsTracker to finish up to avoid potential race condition
+	<-wn.requestsTracker.getWaitUntilNoConnectionsChannel(5 * time.Millisecond)
 	wn.messagesOfInterestMu.Lock()
 	defer wn.messagesOfInterestMu.Unlock()
+
 	wn.messagesOfInterestEncoded = false
 	wn.messagesOfInterestEnc = nil
 	wn.messagesOfInterest = nil
@@ -1111,6 +1114,7 @@ func (wn *WebsocketNetwork) ServeHTTP(response http.ResponseWriter, request *htt
 			InstanceName: trackedRequest.otherInstanceName,
 		})
 
+	// We are careful to encode this prior to starting the server to avoid needing 'messagesOfInterestMu' here.
 	if wn.messagesOfInterestEnc != nil {
 		err = peer.Unicast(wn.ctx, wn.messagesOfInterestEnc, protocol.MsgOfInterestTag)
 		if err != nil {
```
