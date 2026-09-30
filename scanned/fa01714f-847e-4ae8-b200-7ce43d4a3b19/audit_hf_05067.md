# [M] The malicious node may not ex-

## Summary
Severity: Medium
Contest weight: 0.1919
Dataset id: 23078
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
topics_handler will make an http request to call the http api in blockless,
```go
func makeApiCall(payload string) error {
    url := os.Getenv("BLOCKLESS_API_URL")
    method := "POST"
    client := &http.Client{}
    req, err := http.NewRequest(method, url, strings.NewReader(payload))
    if err != nil {
        return err
    }
    req.Header.Add("Accept", "application/json, text/plain, */*")
    req.Header.Add("Content-Type", "application/json;charset=UTF-8")
    res, err := client.Do(req)
    if err != nil {
        return err
    }
    defer res.Body.Close()
    return nil
}
```
It is often dangerous to initiate an http request in a node on a blockchain chain. However, because the operation here is performed in a PrepareProposalHandler, it may not result in direct state inconsistency between different nodes. But the problem here is that the malicious node can not perform this operation, so blockless can not receive http requests. Because other nodes have no way of knowing whether the http request can be successfully executed, the http request may fail due to network problems. Therefore, the malicious node can choose not to execute the http request, so that he can save server-side resources, or in the purpose of attack. The api in blockless cannot be invoked because the malicious node does not execute the http request, causing the protocol to fail to work or affecting blockless working efficiency.

## Recommendation
Let blockless query data from the chain instead of the node on the chain calling blockless.
