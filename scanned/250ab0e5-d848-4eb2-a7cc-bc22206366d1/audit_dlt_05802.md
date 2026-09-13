# [?] fix(state): fixing panic when err != nil but response is nil (#2339)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-06-08
Source: https://github.com/celestiaorg/celestia-node/commit/f632908ebff8a349874d0bca3150ec7ca1ed3da1
Type: security-commit

## Details
fix(state): fixing panic when err != nil but response is nil (#2339)

There was a panic when err != nil but response == nil, for example in
the case of: `rpc error: code = NotFound desc = account
celestia1gchva5av4v798xmqttln9qw9smzrjm2cv2q8e7 not found`

```
2023-06-07T14:20:38.731+0200	ERROR	rpc	go-jsonrpc@v0.3.1/handler.go:276	panic in rpc method 'blob.Submit': runtime error: invalid memory address or nil pointer dereference
```

---------

Co-authored-by: Vlad <13818348+walldiss@users.noreply.github.com>
