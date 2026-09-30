# [M] Lack of Timeout leads Resource

## Summary
Severity: Medium
Contest weight: 0.2714
Dataset id: 23061
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The absence of timeout settings in the HTTP client poses the following risks:
1. Resource Exhaustion:
• Connections may hang indefinitely, leading to goroutine leaks and memory overconsumption.
• Over time, this can cause the application to crash or become unresponsive.
2. Denial of Service (DoS) Vulnerability:
• Attackers could exploit this to overwhelm the system by initiating numerous long-lasting connections.
• This could render the entire application or service unavailable to legitimate users.
3. Cascading Failures:
• In a microservices architecture, hanging connections can lead to cascading failures across multiple services.
• This can result in system-wide outages and difficult-to-diagnose issues.
The current implementation of the makeApiCall function lacks timeout configurations, introducing a severe vulnerability that could lead to resource exhaustion, denial of service, and system instability.
Implementing these timeout configurations will significantly enhance the resilience and security of the API client:
1. Prevent Resource Exhaustion: By limiting the duration of connections, the system can maintain control over resource allocation.
2. Mitigate DoS Vulnerabilities: Timeouts make it much harder for attackers to overwhelm the system with long-lasting connections.
3. Improve System Stability: By avoiding hanging connections, the overall stability and predictability of the system are greatly enhanced.
api.go#L166
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

## Recommendation
Implement comprehensive timeout settings in the HTTP client:
func makeApiCall(payload string) error {
url := os.Getenv("BLOCKLESS_API_URL")
client := &http.Client{
Timeout: 30 * time.Second,
// Overall timeout for the request
Transport: &http.Transport{
DialContext: (&net.Dialer{
Timeout: 5 * time.Second,
// Connection timeout
KeepAlive: 30 * time.Second,
}).DialContext,
TLSHandshakeTimeout: 10 * time.Second,
// TLS handshake timeout
// Timeout for server's
ExpectContinueTimeout: 1 * time.Second,
IdleConnTimeout: 90 * time.Second,
// Idle connection timeout
MaxIdleConnsPerHost: 10,
// Limit idle connections
},
}
ctx, cancel := context.WithTimeout(context.Background(), 25*time.Second)
defer cancel()
req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, strings.NewReader(payload))
if err != nil {
return fmt.Errorf("failed to create request: %w", err)
}
res, err := client.Do(req)
if err != nil {
if os.IsTimeout(err) {
return fmt.Errorf("request timed out: %w", err)
}
return fmt.Errorf("request failed: %w", err)
}
defer res.Body.Close()
// ... (rest of the function)
}
