# [M] DoS via malicious snap/1 request

## Summary
Severity: Medium
Chain: Ethereum
Component: ethereum/go-ethereum
CVE: CVE-2021-41173
Published: 2021-10-25
Source: https://github.com/ethereum/go-ethereum/security/advisories/GHSA-59hh-656j-3p7v
Type: github-advisory

## Details
### Impact

A vulnerable node is susceptible to crash when processing a maliciously crafted message from a peer, via the `snap/1` protocol. The crash can be triggered by sending a malicious `snap/1` `GetTrieNodes` package. 

### Details

On September 21, 2021, geth-team member Gary Rong (@rjl493456442) found a way to crash the snap request handler . 
By using this vulnerability, a peer connected on the `snap/1` protocol could cause a vulnerable node to crash with a `panic`.

In the `trie.TryGetNode` implementation, if the requested path is reached, the associated node will be returned. However the nilness is
not checked there.

```golang
func (t *Trie) tryGetNode(origNode node, path []byte, pos int) (item []byte, newnode node, resolved int, err error) {
	// If we reached the requested path, return the current node
	if pos >= len(path) {
		// Although we most probably have the original node expanded, encoding
		// that into consensus form can be nasty (needs to cascade down) and
		// time consuming. Instead, just pull the hash up from disk directly.
		var hash hashNode
		if node, ok := origNode.(hashNode); ok {
			hash = node
		} else {
			hash, _ = origNode.cache()
		}
```
More specifically the `origNode` can be nil(e.g. the child of fullnode) and system can panic at line `hash, _ = origNode.cache()`. 

When investigating this, @holiman tried to find it via fuzzing, which uncovered a second crasher, also related to the snap `GetTrieNodes` package. If the caller requests a storage trie:
```golang
				// Storage slots requested, open the storage trie and retrieve from there
				account, err := snap.Account(common.BytesToHash(pathset[0]))
				loads++ // always account database reads, even for failures
				if account == nil {
					break
				}
				stTrie, err := trie.NewSecure(common.BytesToHash(account.Root), triedb)
```

_Trimmed to 38 lines — full report: https://github.com/ethereum/go-ethereum/security/advisories/GHSA-59hh-656j-3p7v_
