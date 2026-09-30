# [M] Too high timeout value for HTTP requests

## Summary
Severity: Medium
Contest weight: 0.2509
Dataset id: 1862
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Too high timeout value for HTTP request may cause missed transactions on Solana network because of low amount of fetched transaction. In util.go::HTTP() function, the timeout value is set to 90 seconds for HTTP calls. But this value is too high for error handling situations. In any packet loss situation this timeout value will stop the scanning for 90 seconds. In 90 seconds, it's possible to miss transactions on Solana Network because Solana has a really high BPS rate and 90 seconds is really high timeout value for Solana Network.
```go
func init() {
    http.DefaultClient.Timeout = 90 * time.Second
}

func Http(v interface{}, method, url, bodyString string, headers map[string]string) {
    req, err := http.NewRequest(method, url, bytes.NewBufferString(bodyString))
    if err != nil {
        return err
    }
    req.Header.Set("Accept", "application/json")
    if headers != nil {
        for k, v := range headers {
            req.Header.Set(k, v)
        }
    }
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return fmt.Errorf("Http: call %s: %w", url, err)
    }
    defer resp.Body.Close()
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return fmt.Errorf("Http: read %s: %w", url, err)
    }
    if resp.StatusCode < 200 || resp.StatusCode >= 300 {
        panic(fmt.Errorf(`fetch: code %d: %s: %s`, resp.StatusCode, url, string(body)))
    }
    return json.Unmarshal(body, &v)
}

func (b *Bridge) solScan() []*Transfer {
    // fetch recent transactions that interracted with our program
    transfers := []*Transfer{}
    signatures := solanaRpc("getSignaturesForAddress", Env("SOLANA_PROGRAM", ""), J{"limit": 100}).([]interface{})
    for _, rs := range signatures {
        id := NJ(rs).Get("signature")
        if b.DB.Where("id = ?", id).First(&Transfer{}).Error == nil {
            continue // skip out early to save on requests
        }
        transfers = append(transfers, b.solScanTx(id)...)
    }
    return transfers
}
```
External pre-conditions
1. Timeout situation is happened ( such as packet loss )
Attack Path
This situation can occur in high volatility moments.
1. There are 100 transactions in corresponding Solana Program address
2. Those transactions are fetched by the off-chain protocol
3. Timeout situation is happened
4. Another 200 transactions is submitted by the users
5. Solana executed those transactions before timeout ends
6. Now 100 transactions are lost because off-chain system will detect the last 100 transactions
High - Those transactions can't be detected by the protocol and they can't even solve the problem using the admin panel because the transactions aren't detected and stored in DB
The users lost their funds.

## Recommendation
Apply reasonable amount of timeout for HTTP and use a bigger limit for Solana signature fetch.
Disclaimers
project.
Usage of all smart contract software is at the respective users’ sole risk and is the users’ responsibility.
