# [?] Properly close connection to Constellation to prevent panic (#491)

## Summary
Severity: Unknown
Chain: Quorum
Component: Consensys-inc-archive/quorum
Published: 2018-08-22
Source: https://github.com/Consensys-inc-archive/quorum/commit/64ce540f5df218533b2fd80a5b48696653db92b5
Type: security-commit

## Details
Properly close connection to Constellation to prevent panic (#491)

## Patch
### private/constellation/node.go
```diff
@@ -92,10 +92,17 @@ func (c *Client) SendPayload(pl []byte, b64From string, b64To []string) ([]byte,
 	req.Header.Set("c11n-to", strings.Join(b64To, ","))
 	req.Header.Set("Content-Type", "application/octet-stream")
 	res, err := c.httpClient.Do(req)
-	if err == nil && res.StatusCode != 200 {
+
+	if res != nil {
+		defer res.Body.Close()
+	}
+	if err != nil {
+		return nil, err
+	}
+	if res.StatusCode != 200 {
 		return nil, fmt.Errorf("Non-200 status code: %+v", res)
 	}
-	defer res.Body.Close()
+
 	return ioutil.ReadAll(base64.NewDecoder(base64.StdEncoding, res.Body))
 }
 
@@ -106,10 +113,17 @@ func (c *Client) ReceivePayload(key []byte) ([]byte, error) {
 	}
 	req.Header.Set("c11n-key", base64.StdEncoding.EncodeToString(key))
 	res, err := c.httpClient.Do(req)
-	if err == nil && res.StatusCode != 200 {
+
+	if res != nil {
+		defer res.Body.Close()
+	}
+	if err != nil {
+		return nil, err
+	}
+	if res.StatusCode != 200 {
 		return nil, fmt.Errorf("Non-200 status code: %+v", res)
 	}
-	defer res.Body.Close()
+
 	return ioutil.ReadAll(res.Body)
 }
 
```
