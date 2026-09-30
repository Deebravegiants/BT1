# [?] fix(cometbft): use AddCommit that doesn't panic on failed verification of commit (#3074)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2026-04-07
Source: https://github.com/berachain/beacon-kit/commit/3d8f0d4b2972961c99724973da65adb5f2b27eae
Type: security-commit

## Details
fix(cometbft): use AddCommit that doesn't panic on failed verification of commit (#3074)

## Patch
### go.mod
```diff
@@ -3,8 +3,8 @@ module github.com/berachain/beacon-kit
 go 1.26.1
 
 replace (
-	github.com/cometbft/cometbft => github.com/berachain/cometbft v1.0.1-0.20260120183949-acbb64111633
-	github.com/cometbft/cometbft/api => github.com/berachain/cometbft/api v1.0.1-0.20260120183949-acbb64111633
+	github.com/cometbft/cometbft => github.com/berachain/cometbft v1.0.1-0.20260407160047-b95619676ffc
+	github.com/cometbft/cometbft/api => github.com/berachain/cometbft/api v1.0.1-0.20260407160047-b95619676ffc
 	github.com/cosmos/cosmos-sdk => github.com/cosmos/cosmos-sdk v0.52.0-rc.1
 	github.com/karalabe/ssz => github.com/berachain/karalabe-ssz v0.3.0-alpha.0
 )
```

### go.sum
```diff
@@ -78,10 +78,10 @@ github.com/beorn7/perks v0.0.0-20180321164747-3a771d992973/go.mod h1:Dwedo/Wpr24
 github.com/beorn7/perks v1.0.0/go.mod h1:KWe93zE9D1o94FZ5RNwFwVgaQK1VOXiVxmqh+CedLV8=
 github.com/beorn7/perks v1.0.1 h1:VlbKKnNfV8bJzeqoa4cOKqO6bYr3WgKZxO8Z16+hsOM=
 github.com/beorn7/perks v1.0.1/go.mod h1:G2ZrVWU2WbWT9wwq4/hrbKbnv/1ERSJQ0ibhJ6rlkpw=
-github.com/berachain/cometbft v1.0.1-0.20260120183949-acbb64111633 h1:Y5KD4v+JIfJA4BcKY/EQETTPczp6fdAW8rD1NsLk2OI=
-github.com/berachain/cometbft v1.0.1-0.20260120183949-acbb64111633/go.mod h1:AB3j5W0TQmQSuwRdzWvIBQPAKquFo7VnckwETlAsuwk=
-github.com/berachain/cometbft/api v1.0.1-0.20260120183949-acbb64111633 h1:Zkrk9gr1MAyjGHhQV2SRf5KqE3E1g9N5XCEahB13/YY=
-github.com/berachain/cometbft/api v1.0.1-0.20260120183949-acbb64111633/go.mod h1:QaK8NCB4rHDs0MdS+L+QOQsL4UM3YJ9OMCNrH+CGdA0=
+github.com/berachain/cometbft v1.0.1-0.20260407160047-b95619676ffc h1:oO099KFHn5l8jBs5YQnC6dowtFQqXDYY2wo8RQBnojk=
+github.com/berachain/cometbft v1.0.1-0.20260407160047-b95619676ffc/go.mod h1:AB3j5W0TQmQSuwRdzWvIBQPAKquFo7VnckwETlAsuwk=
+github.com/berachain/cometbft/api v1.0.1-0.20260407160047-b95619676ffc h1:XZlAYs0qgKJ9209eFEDwxKLiXqeRwn39LgjSrRxHZZc=
+github.com/berachain/cometbft/api v1.0.1-0.20260407160047-b95619676ffc/go.mod h1:QaK8NCB4rHDs0MdS+L+QOQsL4UM3YJ9OMCNrH+CGdA0=
 github.com/berachain/karalabe-ssz v0.3.0-alpha.0 h1:SVMU5PSuMB2fgmFTf1rSBY9rEHpQv24DJcqxSrD7jf8=
 github.com/berachain/karalabe-ssz v0.3.0-alpha.0/go.mod h1:7BZG/jckt43eKw7sl/AF6gTcL0oxgFPme39m54v8rDI=
 github.com/bgentry/speakeasy v0.2.0 h1:tgObeVOf8WAvtuAX6DhJ4xks4CFNwPDZiqzGqIHE51E=
```
