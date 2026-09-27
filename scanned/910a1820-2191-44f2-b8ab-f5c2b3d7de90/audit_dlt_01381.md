# [?] eth/downloader: fixes data race between synchronize and other methods (#21201)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-06-30
Source: https://github.com/celo-org/celo-blockchain/commit/d671dbd5b79d2213b92c2c187b9016c4309881c9
Type: security-commit

## Details
eth/downloader: fixes data race between synchronize and other methods (#21201)

* eth/downloaded: fixed datarace between synchronize and Progress

There was a race condition between `downloader.synchronize()` and `Progress` `syncWithPeer` `fetchHeight` `findAncestors` and `processHeaders`
This PR changes the behavior of the downloader a bit.
Previously the functions `Progress` `syncWithPeer` `fetchHeight` `findAncestors` and `processHeaders` read the syncMode anew within their loops. Now they read the syncMode at the start of their function and don't change it during their runtime.

* eth/downloaded: comment

* eth/downloader: added comment
