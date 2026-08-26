# [?] rpcclient: fix race condition in `doDisconnect`

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2023-12-31
Source: https://github.com/btcsuite/btcd/commit/4ec8f016b99d7295313c1d2b094033daf447ab11
Type: security-commit

## Details
rpcclient: fix race condition in `doDisconnect`

In this commit, we fix the following race condition:
```
==================
WARNING: DATA RACE
Write at 0x00c000216018 by goroutine 31:
  github.com/btcsuite/btcd/rpcclient.(*Client).wsReconnectHandler()
      /home/runner/work/btcd/btcd/rpcclient/infrastructure.go:736 +0x2aa
  github.com/btcsuite/btcd/rpcclient.New·dwrap·13()
      /home/runner/work/btcd/btcd/rpcclient/infrastructure.go:1496 +0x39

Previous read at 0x00c000216018 by goroutine 29:
  github.com/btcsuite/btcd/rpcclient.(*Client).doDisconnect()
      /home/runner/work/btcd/btcd/rpcclient/infrastructure.go:1079 +0x247
  github.com/btcsuite/btcd/rpcclient.(*Client).Disconnect()
      /home/runner/work/btcd/btcd/rpcclient/infrastructure.go:1111 +0x47
  github.com/btcsuite/btcd/rpcclient.(*Client).wsInHandler()
      /home/runner/work/btcd/btcd/rpcclient/infrastructure.go:491 +0x1eb
  github.com/btcsuite/btcd/rpcclient.(*Client).start·dwrap·11()
      /home/runner/work/btcd/btcd/rpcclient/infrastructure.go:1181 +0x39

Goroutine 31 (running) created at:
  github.com/btcsuite/btcd/rpcclient.New()
      /home/runner/work/btcd/btcd/rpcclient/infrastructure.go:1496 +0xd77
  github.com/btcsuite/btcd/rpcclient.makeClient()
      /home/runner/work/btcd/btcd/rpcclient/chain_test.go:268 +0x1f9
  github.com/btcsuite/btcd/rpcclient.TestClientConnectedToWSServerRunner.func2()
      /home/runner/work/btcd/btcd/rpcclient/chain_test.go:164 +0x47
  testing.tRunner()
      /opt/hostedtoolcache/go/1.17.5/x64/src/testing/testing.go:1259 +0x22f
  testing.(*T).Run·dwrap·21()
      /opt/hostedtoolcache/go/1.17.5/x64/src/testing/testing.go:1306 +0x47

Goroutine 29 (finished) created at:
  github.com/btcsuite/btcd/rpcclient.(*Client).start()
      /home/runner/work/btcd/btcd/rpcclient/infrastructure.go:1181 +0x2e4
  github.com/btcsuite/btcd/rpcclient.New()
```

_Trimmed to 38 lines — full report: https://github.com/btcsuite/btcd/commit/4ec8f016b99d7295313c1d2b094033daf447ab11_
