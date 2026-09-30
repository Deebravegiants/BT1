# [M] Outdated dc4bc Dependencies and Forks

## Summary
Severity: Medium
Contest weight: 0.2444
Dataset id: 14388
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In its go.mod file, dc4bc specifies several outdated dependencies and the following replace directive:  
replace golang.org/x/crypto => github.com/tendermint/crypto v0.0.0-20180820045704-3764759f34a5  
This directive replaces all imports of the standard golang.org/x/crypto library with the unmaintained tendermint/crypto fork, including in all dependencies3 Fortunately, no relevant security vulnerabilities were found that affect code used by dc4bc.4 We note that the random seed functionality exposed by the fork is not needed by dc4bc or any dependencies.5 Refer to ./tools-output/dc4bc-deps.out and ./tools-output/kyber-deps.out provided to the development team in addition to this report. While cryptography libraries are quite heavily scrutinized and the dc4bc use-case prioritizes backwards compatibility over availability/performance, it is of paramount importance that any security issues in dependencies are reviewed and acknowledged. The security risk identified here is less about the current dependency versions, and more the update and security alerting processes in place for dc4bc.  
3 corestario/kyber uses x/crypto in the following files:  
sign/bdn/bdn.go: "golang.org/x/crypto/blake2s"  
xof/keccak/keccak.go: "golang.org/x/crypto/sha3"  
share/vss/pedersen/dh.go: "golang.org/x/crypto/hkdf"  
share/vss/rabin/dh.go: "golang.org/x/crypto/hkdf"  
xof/blake2xb/blake.go: "golang.org/x/crypto/blake2b"  
xof/blake2xs/blake.go: "golang.org/x/crypto/blake2s"  
pairing/bn256/suite_test.go: "golang.org/x/crypto/bn256"  
encrypt/ecies/ecies.go: "golang.org/x/crypto/hkdf"  
dc4bc:  
opdos=0&opec=0&opov=0&opcsrf=0&opgpriv=0&opsqli=0&opxss=0&opdirt=0&opmemc=0&ophttprs=0&opbyp=0&opfileinc=0&  
opginf=0&cvssscoremin=0&cvssscoremax=0&year=0&cweid=0&order=1&trc=31&sha=28620af5fce730868aaad8eb6b0b82bc3b861475  
5 Refer to the following to note changes introduced by the fork, and updates since:  
Lido Finance Security Assessment

## Recommendation
Remove the unneeded replace directive for golang.org/x/crypto. Update relevant dependencies, and consider introducing monitoring to alert for vulnerabilities in associated dependencies.
