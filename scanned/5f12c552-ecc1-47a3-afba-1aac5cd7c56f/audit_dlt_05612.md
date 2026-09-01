# [?] fix: PatriciaTree commit deadlock on bounded scheduler (#11299)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-04-22
Source: https://github.com/NethermindEth/nethermind/commit/3e8bbfce08e990493503a37e53149f0a6ddbff92
Type: security-commit

## Details
fix: PatriciaTree commit deadlock on bounded scheduler (#11299)

* refactor: optimize task creation for path commits in PatriciaTree

* refactor: replace Task.Factory.StartNew with Task.Run for improved task creation in PatriciaTree

* retrun back factory

* fix: always return concurrency quota on commit failure in PatriciaTree

* test: add test to ensure commit does not deadlock on bounded scheduler in PatriciaTree

* Update src/Nethermind/Nethermind.Trie/PatriciaTree.cs

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>

---------

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>
