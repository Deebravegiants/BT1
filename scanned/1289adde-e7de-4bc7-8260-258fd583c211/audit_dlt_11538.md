# [?] fix(cert-verifier): simplify checkSecurityParams implementation to prevent divide-by-zero panic case (#2173)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2025-10-22
Source: https://github.com/Layr-Labs/eigenda/commit/dbfdcbba385009efb1e87328f172ffdcdff2a25a
Type: security-commit

## Details
fix(cert-verifier): simplify checkSecurityParams implementation to prevent divide-by-zero panic case (#2173)

* refactor: simplify security-threshold equation, remove division, and update documentation

* Update docs/spec/src/protocol/architecture/security-parameters.md

Co-authored-by: Samuel Laferriere <9342524+samlaf@users.noreply.github.com>

* Update docs/spec/src/protocol/architecture/security-parameters.md

Co-authored-by: Samuel Laferriere <9342524+samlaf@users.noreply.github.com>

* revert changes in legacy code

* add underflow check for maxNumOperators > numChunks in security threshold check and update doc

* resolve CI lint and formatting errors in contracts

* remove old code and comments in security threshold check function

* * fix: ensure that confirmation threshold >= safety threshold to avoid underflow
* doc: simplify the code block in doc and update link to code

* add unit test for security threshold check

* remove contracts/foundry.lock; generate new bindings

* Update docs/spec/src/protocol/architecture/security-parameters.md

fix typo

Co-authored-by: Samuel Laferriere <9342524+samlaf@users.noreply.github.com>

---------

Co-authored-by: Samuel Laferriere <9342524+samlaf@users.noreply.github.com>

## Patch
### api/clients/v2/verification/contract_status_codes.go
```diff
@@ -46,7 +46,7 @@ func (s CheckDACertStatusCode) String() string {
 	case StatusInvalidInclusionProof:
 		return "Invalid inclusion proof detected: Merkle inclusion proof for blob batch is invalid"
 	case StatusSecurityAssumptionsNotMet:
-		return "Security assumptions not met: BLS signer weight is less than the required threshold"
+		return "Security assumptions not met: The security parameters do not pass the check. For more info read eigenda/docs/spec/src/protocol/architecture/security-parameters.md"
 	case StatusBlobQuorumsNotSubset:
 		return "Blob quorums are not a subset of the confirmed quorums"
 	case StatusRequiredQuorumsNotSubset:
```

### contracts/bindings/EigenDACertVerifier/binding.go
```diff
@@ -105,7 +105,7 @@ type EigenDATypesV2BlobInclusionInfo struct {
 
 // ContractEigenDACertVerifierMetaData contains all meta data concerning the ContractEigenDACertVerifier contract.
 var ContractEigenDACertVerifierMetaData = &bind.MetaData{
-	ABI: "[{\"type\":\"constructor\",\"inputs\":[{\"name\":\"initEigenDAThresholdRegistry\",\"type\":\"address\",\"internalType\":\"contractIEigenDAThresholdRegistry\"},{\"name\":\"initEigenDASignatureVerifier\",\"type\":\"address\",\"internalType\":\"contractIEigenDASignatureVerifier\"},{\"name\":\"initSecurityThresholds\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.SecurityThresholds\",\"components\":[{\"name\":\"confirmationThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"adversaryThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"}]},{\"name\":\"initQuorumNumbersRequired\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"_decodeCert\",\"inputs\":[{\"name\":\"data\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"outputs\":[{\"name\":\"cert\",\"type\":\"tuple\",\"internalType\":\"structEigenDACertTypes.EigenDACertV3\",\"components\":[{\"name\":\"batchHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BatchHeaderV2\",\"components\":[{\"name\":\"batchRoot\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"referenceBlockNumber\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"blobInclusionInfo\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobInclusionInfo\",\"components\":[{\"name\":\"blobCertificate\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCertificate\",\"components\":[{\"name\":\"blobHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobHeaderV2\",\"components\":[{\"name\":\"version\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"quorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCommitment\",\"components\":[{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"lengthCommitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"lengthProof\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"length\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"paymentHeaderHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"name\":\"signature\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"relayKeys\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"}]},{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"inclusionProof\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"nonSignerStakesAndSignature\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.NonSignerStakesAndSignature\",\"components\":[{\"name\":\"nonSignerQuorumBitmapIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerPubkeys\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApks\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"apkG2\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"sigma\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApkIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"totalStakeIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerStakeIndices\",\"type\":\"uint32[][]\",\"internalType\":\"uint32[][]\"}]},{\"name\":\"signedQuorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]}],\"stateMutability\":\"pure\"},{\"type\":\"function\",\"name\":\"certVersion\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"pure\"},{\"type\":\"function\",\"name\":\"checkDACert\",\"inputs\":[{\"name\":\"abiEncodedCert\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"outputs\":[{\"name\":\"\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"checkDACertReverts\",\"inputs\":[{\"name\":\"daCert\",\"type\":\"tuple\",\"internalType\":\"structEigenDACertTypes.EigenDACertV3\",\"components\":[{\"name\":\"batchHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BatchHeaderV2\",\"components\":[{\"name\":\"batchRoot\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"referenceBlockNumber\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"blobInclusionInfo\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobInclusionInfo\",\"components\":[{\"name\":\"blobCertificate\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCertificate\",\"components\":[{\"name\":\"blobHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobHeaderV2\",\"components\":[{\"name\":\"version\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"quorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCommitment\",\"components\":[{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"lengthCommitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"lengthProof\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"length\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"paymentHeaderHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"name\":\"signature\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"relayKeys\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"}]},{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"inclusionProof\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"nonSignerStakesAndSignature\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.NonSignerStakesAndSignature\",\"components\":[{\"name\":\"nonSignerQuorumBitmapIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerPubkeys\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApks\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"apkG2\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"sigma\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApkIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"totalStakeIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerStakeIndices\",\"type\":\"uint32[][]\",\"internalType\":\"uint32[][]\"}]},{\"name\":\"signedQuorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]}],\"outputs\":[],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"eigenDASignatureVerifier\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"contractIEigenDASignatureVerifier\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"eigenDAThresholdRegistry\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"contractIEigenDAThresholdRegistry\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"quorumNumbersRequired\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"securityThresholds\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.SecurityThresholds\",\"components\":[{\"name\":\"confirmationThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"adversaryThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"}]}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"semver\",\"inputs\":[],\"outputs\":[{\"name\":\"major\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"minor\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"patch\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"pure\"},{\"type\":\"error\",\"name\":\"BlobQuorumsNotSubset\",\"inputs\":[{\"name\":\"blobQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"confirmedQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"InvalidBlobVersion\",\"inputs\":[{\"name\":\"blobVersion\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"nextBlobVersion\",\"type\":\"uint16\",\"internalType\":\"uint16\"}]},{\"type\":\"error\",\"name\":\"InvalidInclusionProof\",\"inputs\":[{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"blobHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"rootHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"type\":\"error\",\"name\":\"InvalidQuorumNumbersRequired\",\"inputs\":[{\"name\":\"length\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"InvalidSecurityThresholds\",\"inputs\":[]},{\"type\":\"error\",\"name\":\"RequiredQuorumsNotSubset\",\"inputs\":[{\"name\":\"requiredQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"blobQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"SecurityAssumptionsNotMet\",\"inputs\":[{\"name\":\"gamma\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"n\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"minRequired\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]}]",
+	ABI: "[{\"type\":\"constructor\",\"inputs\":[{\"name\":\"initEigenDAThresholdRegistry\",\"type\":\"address\",\"internalType\":\"contractIEigenDAThresholdRegistry\"},{\"name\":\"initEigenDASignatureVerifier\",\"type\":\"address\",\"internalType\":\"contractIEigenDASignatureVerifier\"},{\"name\":\"initSecurityThresholds\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.SecurityThresholds\",\"components\":[{\"name\":\"confirmationThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"adversaryThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"}]},{\"name\":\"initQuorumNumbersRequired\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"_decodeCert\",\"inputs\":[{\"name\":\"data\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"outputs\":[{\"name\":\"cert\",\"type\":\"tuple\",\"internalType\":\"structEigenDACertTypes.EigenDACertV3\",\"components\":[{\"name\":\"batchHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BatchHeaderV2\",\"components\":[{\"name\":\"batchRoot\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"referenceBlockNumber\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"blobInclusionInfo\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobInclusionInfo\",\"components\":[{\"name\":\"blobCertificate\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCertificate\",\"components\":[{\"name\":\"blobHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobHeaderV2\",\"components\":[{\"name\":\"version\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"quorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCommitment\",\"components\":[{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"lengthCommitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"lengthProof\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"length\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"paymentHeaderHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"name\":\"signature\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"relayKeys\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"}]},{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"inclusionProof\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"nonSignerStakesAndSignature\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.NonSignerStakesAndSignature\",\"components\":[{\"name\":\"nonSignerQuorumBitmapIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerPubkeys\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApks\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"apkG2\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"sigma\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApkIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"totalStakeIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerStakeIndices\",\"type\":\"uint32[][]\",\"internalType\":\"uint32[][]\"}]},{\"name\":\"signedQuorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]}],\"stateMutability\":\"pure\"},{\"type\":\"function\",\"name\":\"certVersion\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"pure\"},{\"type\":\"function\",\"name\":\"checkDACert\",\"inputs\":[{\"name\":\"abiEncodedCert\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"outputs\":[{\"name\":\"\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"checkDACertReverts\",\"inputs\":[{\"name\":\"daCert\",\"type\":\"tuple\",\"internalType\":\"structEigenDACertTypes.EigenDACertV3\",\"components\":[{\"name\":\"batchHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BatchHeaderV2\",\"components\":[{\"name\":\"batchRoot\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"referenceBlockNumber\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"blobInclusionInfo\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobInclusionInfo\",\"components\":[{\"name\":\"blobCertificate\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCertificate\",\"components\":[{\"name\":\"blobHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobHeaderV2\",\"components\":[{\"name\":\"version\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"quorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCommitment\",\"components\":[{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"lengthCommitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"lengthProof\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"length\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"paymentHeaderHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"name\":\"signature\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"relayKeys\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"}]},{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"inclusionProof\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"nonSignerStakesAndSignature\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.NonSignerStakesAndSignature\",\"components\":[{\"name\":\"nonSignerQuorumBitmapIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerPubkeys\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApks\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"apkG2\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"sigma\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApkIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"totalStakeIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerStakeIndices\",\"type\":\"uint32[][]\",\"internalType\":\"uint32[][]\"}]},{\"name\":\"signedQuorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]}],\"outputs\":[],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"eigenDASignatureVerifier\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"contractIEigenDASignatureVerifier\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"eigenDAThresholdRegistry\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"contractIEigenDAThresholdRegistry\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"quorumNumbersRequired\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"securityThresholds\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.SecurityThresholds\",\"components\":[{\"name\":\"confirmationThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"adversaryThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"}]}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"semver\",\"inputs\":[],\"outputs\":[{\"name\":\"major\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"minor\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"patch\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"pure\"},{\"type\":\"error\",\"name\":\"BlobQuorumsNotSubset\",\"inputs\":[{\"name\":\"blobQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"confirmedQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"InvalidBlobVersion\",\"inputs\":[{\"name\":\"blobVersion\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"nextBlobVersion\",\"type\":\"uint16\",\"internalType\":\"uint16\"}]},{\"type\":\"error\",\"name\":\"InvalidInclusionProof\",\"inputs\":[{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"blobHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"rootHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"type\":\"error\",\"name\":\"InvalidQuorumNumbersRequired\",\"inputs\":[{\"name\":\"length\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"InvalidSecurityThresholds\",\"inputs\":[]},{\"type\":\"error\",\"name\":\"RequiredQuorumsNotSubset\",\"inputs\":[{\"name\":\"requiredQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"blobQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"SecurityAssumptionsNotMet\",\"inputs\":[{\"name\":\"confirmationThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"adversaryThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"codingRate\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"numChunks\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"maxNumOperators\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]}]",
 }
 
 // ContractEigenDACertVerifierABI is the input ABI used to generate the binding from.
```

### contracts/bindings/v2/EigenDACertVerifier/binding.go
```diff
@@ -100,7 +100,7 @@ type EigenDATypesV2BlobInclusionInfo struct {
 
 // ContractEigenDACertVerifierMetaData contains all meta data concerning the ContractEigenDACertVerifier contract.
 var ContractEigenDACertVerifierMetaData = bind.MetaData{
-	ABI: "[{\"type\":\"constructor\",\"inputs\":[{\"name\":\"initEigenDAThresholdRegistry\",\"type\":\"address\",\"internalType\":\"contractIEigenDAThresholdRegistry\"},{\"name\":\"initEigenDASignatureVerifier\",\"type\":\"address\",\"internalType\":\"contractIEigenDASignatureVerifier\"},{\"name\":\"initSecurityThresholds\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.SecurityThresholds\",\"components\":[{\"name\":\"confirmationThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"adversaryThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"}]},{\"name\":\"initQuorumNumbersRequired\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"_decodeCert\",\"inputs\":[{\"name\":\"data\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"outputs\":[{\"name\":\"cert\",\"type\":\"tuple\",\"internalType\":\"structEigenDACertTypes.EigenDACertV3\",\"components\":[{\"name\":\"batchHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BatchHeaderV2\",\"components\":[{\"name\":\"batchRoot\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"referenceBlockNumber\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"blobInclusionInfo\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobInclusionInfo\",\"components\":[{\"name\":\"blobCertificate\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCertificate\",\"components\":[{\"name\":\"blobHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobHeaderV2\",\"components\":[{\"name\":\"version\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"quorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCommitment\",\"components\":[{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"lengthCommitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"lengthProof\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"length\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"paymentHeaderHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"name\":\"signature\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"relayKeys\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"}]},{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"inclusionProof\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"nonSignerStakesAndSignature\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.NonSignerStakesAndSignature\",\"components\":[{\"name\":\"nonSignerQuorumBitmapIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerPubkeys\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApks\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"apkG2\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"sigma\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApkIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"totalStakeIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerStakeIndices\",\"type\":\"uint32[][]\",\"internalType\":\"uint32[][]\"}]},{\"name\":\"signedQuorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]}],\"stateMutability\":\"pure\"},{\"type\":\"function\",\"name\":\"certVersion\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"pure\"},{\"type\":\"function\",\"name\":\"checkDACert\",\"inputs\":[{\"name\":\"abiEncodedCert\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"outputs\":[{\"name\":\"\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"checkDACertReverts\",\"inputs\":[{\"name\":\"daCert\",\"type\":\"tuple\",\"internalType\":\"structEigenDACertTypes.EigenDACertV3\",\"components\":[{\"name\":\"batchHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BatchHeaderV2\",\"components\":[{\"name\":\"batchRoot\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"referenceBlockNumber\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"blobInclusionInfo\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobInclusionInfo\",\"components\":[{\"name\":\"blobCertificate\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCertificate\",\"components\":[{\"name\":\"blobHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobHeaderV2\",\"components\":[{\"name\":\"version\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"quorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCommitment\",\"components\":[{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"lengthCommitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"lengthProof\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"length\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"paymentHeaderHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"name\":\"signature\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"relayKeys\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"}]},{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"inclusionProof\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"nonSignerStakesAndSignature\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.NonSignerStakesAndSignature\",\"components\":[{\"name\":\"nonSignerQuorumBitmapIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerPubkeys\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApks\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"apkG2\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"sigma\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApkIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"totalStakeIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerStakeIndices\",\"type\":\"uint32[][]\",\"internalType\":\"uint32[][]\"}]},{\"name\":\"signedQuorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]}],\"outputs\":[],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"eigenDASignatureVerifier\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"contractIEigenDASignatureVerifier\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"eigenDAThresholdRegistry\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"contractIEigenDAThresholdRegistry\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"quorumNumbersRequired\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"securityThresholds\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.SecurityThresholds\",\"components\":[{\"name\":\"confirmationThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"adversaryThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"}]}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"semver\",\"inputs\":[],\"outputs\":[{\"name\":\"major\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"minor\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"patch\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"pure\"},{\"type\":\"error\",\"name\":\"BlobQuorumsNotSubset\",\"inputs\":[{\"name\":\"blobQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"confirmedQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"InvalidBlobVersion\",\"inputs\":[{\"name\":\"blobVersion\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"nextBlobVersion\",\"type\":\"uint16\",\"internalType\":\"uint16\"}]},{\"type\":\"error\",\"name\":\"InvalidInclusionProof\",\"inputs\":[{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"blobHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"rootHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"type\":\"error\",\"name\":\"InvalidQuorumNumbersRequired\",\"inputs\":[{\"name\":\"length\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"InvalidSecurityThresholds\",\"inputs\":[]},{\"type\":\"error\",\"name\":\"RequiredQuorumsNotSubset\",\"inputs\":[{\"name\":\"requiredQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"blobQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"SecurityAssumptionsNotMet\",\"inputs\":[{\"name\":\"gamma\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"n\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"minRequired\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]}]",
+	ABI: "[{\"type\":\"constructor\",\"inputs\":[{\"name\":\"initEigenDAThresholdRegistry\",\"type\":\"address\",\"internalType\":\"contractIEigenDAThresholdRegistry\"},{\"name\":\"initEigenDASignatureVerifier\",\"type\":\"address\",\"internalType\":\"contractIEigenDASignatureVerifier\"},{\"name\":\"initSecurityThresholds\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.SecurityThresholds\",\"components\":[{\"name\":\"confirmationThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"adversaryThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"}]},{\"name\":\"initQuorumNumbersRequired\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"_decodeCert\",\"inputs\":[{\"name\":\"data\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"outputs\":[{\"name\":\"cert\",\"type\":\"tuple\",\"internalType\":\"structEigenDACertTypes.EigenDACertV3\",\"components\":[{\"name\":\"batchHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BatchHeaderV2\",\"components\":[{\"name\":\"batchRoot\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"referenceBlockNumber\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"blobInclusionInfo\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobInclusionInfo\",\"components\":[{\"name\":\"blobCertificate\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCertificate\",\"components\":[{\"name\":\"blobHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobHeaderV2\",\"components\":[{\"name\":\"version\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"quorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCommitment\",\"components\":[{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"lengthCommitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"lengthProof\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"length\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"paymentHeaderHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"name\":\"signature\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"relayKeys\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"}]},{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"inclusionProof\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"nonSignerStakesAndSignature\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.NonSignerStakesAndSignature\",\"components\":[{\"name\":\"nonSignerQuorumBitmapIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerPubkeys\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApks\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"apkG2\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"sigma\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApkIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"totalStakeIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerStakeIndices\",\"type\":\"uint32[][]\",\"internalType\":\"uint32[][]\"}]},{\"name\":\"signedQuorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]}],\"stateMutability\":\"pure\"},{\"type\":\"function\",\"name\":\"certVersion\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"pure\"},{\"type\":\"function\",\"name\":\"checkDACert\",\"inputs\":[{\"name\":\"abiEncodedCert\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"outputs\":[{\"name\":\"\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"checkDACertReverts\",\"inputs\":[{\"name\":\"daCert\",\"type\":\"tuple\",\"internalType\":\"structEigenDACertTypes.EigenDACertV3\",\"components\":[{\"name\":\"batchHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BatchHeaderV2\",\"components\":[{\"name\":\"batchRoot\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"referenceBlockNumber\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"blobInclusionInfo\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobInclusionInfo\",\"components\":[{\"name\":\"blobCertificate\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCertificate\",\"components\":[{\"name\":\"blobHeader\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobHeaderV2\",\"components\":[{\"name\":\"version\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"quorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV2.BlobCommitment\",\"components\":[{\"name\":\"commitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"lengthCommitment\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"lengthProof\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"length\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]},{\"name\":\"paymentHeaderHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"name\":\"signature\",\"type\":\"bytes\",\"internalType\":\"bytes\"},{\"name\":\"relayKeys\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"}]},{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"inclusionProof\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"nonSignerStakesAndSignature\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.NonSignerStakesAndSignature\",\"components\":[{\"name\":\"nonSignerQuorumBitmapIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerPubkeys\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApks\",\"type\":\"tuple[]\",\"internalType\":\"structBN254.G1Point[]\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"apkG2\",\"type\":\"tuple\",\"internalType\":\"structBN254.G2Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"Y\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"}]},{\"name\":\"sigma\",\"type\":\"tuple\",\"internalType\":\"structBN254.G1Point\",\"components\":[{\"name\":\"X\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"Y\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"name\":\"quorumApkIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"totalStakeIndices\",\"type\":\"uint32[]\",\"internalType\":\"uint32[]\"},{\"name\":\"nonSignerStakeIndices\",\"type\":\"uint32[][]\",\"internalType\":\"uint32[][]\"}]},{\"name\":\"signedQuorumNumbers\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]}],\"outputs\":[],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"eigenDASignatureVerifier\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"contractIEigenDASignatureVerifier\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"eigenDAThresholdRegistry\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"contractIEigenDAThresholdRegistry\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"quorumNumbersRequired\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"bytes\",\"internalType\":\"bytes\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"securityThresholds\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"tuple\",\"internalType\":\"structEigenDATypesV1.SecurityThresholds\",\"components\":[{\"name\":\"confirmationThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"adversaryThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"}]}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"semver\",\"inputs\":[],\"outputs\":[{\"name\":\"major\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"minor\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"patch\",\"type\":\"uint8\",\"internalType\":\"uint8\"}],\"stateMutability\":\"pure\"},{\"type\":\"error\",\"name\":\"BlobQuorumsNotSubset\",\"inputs\":[{\"name\":\"blobQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"confirmedQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"InvalidBlobVersion\",\"inputs\":[{\"name\":\"blobVersion\",\"type\":\"uint16\",\"internalType\":\"uint16\"},{\"name\":\"nextBlobVersion\",\"type\":\"uint16\",\"internalType\":\"uint16\"}]},{\"type\":\"error\",\"name\":\"InvalidInclusionProof\",\"inputs\":[{\"name\":\"blobIndex\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"blobHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"},{\"name\":\"rootHash\",\"type\":\"bytes32\",\"internalType\":\"bytes32\"}]},{\"type\":\"error\",\"name\":\"InvalidQuorumNumbersRequired\",\"inputs\":[{\"name\":\"length\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"InvalidSecurityThresholds\",\"inputs\":[]},{\"type\":\"error\",\"name\":\"RequiredQuorumsNotSubset\",\"inputs\":[{\"name\":\"requiredQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"blobQuorumsBitmap\",\"type\":\"uint256\",\"internalType\":\"uint256\"}]},{\"type\":\"error\",\"name\":\"SecurityAssumptionsNotMet\",\"inputs\":[{\"name\":\"confirmationThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"adversaryThreshold\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"codingRate\",\"type\":\"uint8\",\"internalType\":\"uint8\"},{\"name\":\"numChunks\",\"type\":\"uint32\",\"internalType\":\"uint32\"},{\"name\":\"maxNumOperators\",\"type\":\"uint32\",\"internalType\":\"uint32\"}]}]",
 	ID:  "ContractEigenDACertVerifier",
 }
 
@@ -626,22 +626,24 @@ func (contractEigenDACertVerifier *ContractEigenDACertVerifier) UnpackRequiredQu
 
 // ContractEigenDACertVerifierSecurityAssumptionsNotMet represents a SecurityAssumptionsNotMet error raised by the ContractEigenDACertVerifier contract.
 type ContractEigenDACertVerifierSecurityAssumptionsNotMet struct {
-	Gamma       *big.Int
-	N           *big.Int
-	MinRequired *big.Int
+	ConfirmationThreshold uint8
+	AdversaryThreshold    uint8
+	CodingRate            uint8
+	NumChunks             uint32
+	MaxNumOperators       uint32
 }
 
 // ErrorID returns the hash of canonical representation of the error's signature.
 //
-// Solidity: error SecurityAssumptionsNotMet(uint256 gamma, uint256 n, uint256 minRequired)
+// Solidity: error SecurityAssumptionsNotMet(uint8 confirmationThreshold, uint8 adversaryThreshold, uint8 codingRate, uint32 numChunks, uint32 maxNumOperators)
 func ContractEigenDACertVerifierSecurityAssumptionsNotMetErrorID() common.Hash {
-	return common.HexToHash("0xff246ca6711037300d8d326f2b42fd9d514d2d0d56be9c7c2a563f5d4a9a6ba3")
+	return common.HexToHash("0xf6a44993484a4a6b12403f546a5fe315b0c0c33758393492fac6fbb2a437bd9a")
 }
 
 // UnpackSecurityAssumptionsNotMetError is the Go binding used to decode the provided
 // error data into the corresponding Go error struct.
 //
-// Solidity: error SecurityAssumptionsNotMet(uint256 gamma, uint256 n, uint256 minRequired)
+// Solidity: error SecurityAssumptionsNotMet(uint8 confirmationThreshold, uint8 adversaryThreshold, uint8 codingRate, uint32 numChunks, uint32 maxNumOperators)
 func (contractEigenDACertVerifier *ContractEigenDACertVerifier) UnpackSecurityAssumptionsNotMetError(raw []byte) (*ContractEigenDACertVerifierSecurityAssumptionsNotMet, error) {
 	out := new(ContractEigenDACertVerifierSecurityAssumptionsNotMet)
 	if err := contractEigenDACertVerifier.abi.UnpackIntoInterface(out, "SecurityAssumptionsNotMet", raw); err != nil {
```

### contracts/package.json
```diff
@@ -26,5 +26,6 @@
   "dependencies": {
     "@openzeppelin/contracts": "4.7.0",
     "@openzeppelin/contracts-upgradeable": "4.7.0"
-  }
+  },
+  "packageManager": "yarn@1.22.22+sha512.a6b2f7906b721bba3d67d4aff083df04dad64c399707841b7acf00f6b133b7ac24255f2652fa22ae3534329dc6180534e98d17432037ff6fd140556e2bb3137e"
 }
```

### contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol
```diff
@@ -29,10 +29,18 @@ library EigenDACertVerificationLib {
     error InvalidInclusionProof(uint32 blobIndex, bytes32 blobHash, bytes32 rootHash);
 
     /// @notice Thrown when security assumptions are not met
-    /// @param gamma The difference between confirmation and adversary thresholds
-    /// @param n The calculated security parameter
-    /// @param minRequired The minimum required value for n
-    error SecurityAssumptionsNotMet(uint256 gamma, uint256 n, uint256 minRequired);
+    /// @param confirmationThreshold The confirmation threshold percentage
+    /// @param adversaryThreshold The safety threshold percentage
+    /// @param codingRate The coding rate for the blob
+    /// @param numChunks The number of chunks in the blob
+    /// @param maxNumOperators The maximum number of operators
+    error SecurityAssumptionsNotMet(
+        uint8 confirmationThreshold,
+        uint8 adversaryThreshold,
+        uint8 codingRate,
+        uint32 numChunks,
+        uint32 maxNumOperators
+    );
 
     /// @notice Thrown when blob quorums are not a subset of confirmed quorums
     /// @param blobQuorumsBitmap The bitmap of blob quorums
@@ -146,8 +154,7 @@ library EigenDACertVerificationLib {
      * @notice Checks the security parameters for a blob cert
      * @dev Verifies that the security condition
      *      (confirmationThreshold - adversaryThreshold > reconstructionThreshold)
-     *      holds, by checking the invariant
-     *      `numChunks * (1 - 100/gamma/codingRate) >= maxNumOperators`
+     *      holds, by checking an invariant.
      *      If the inequality fails, the blob is considered insecure.
      * @param eigenDAThresholdRegistry The threshold registry contract
      * @param blobVersion The blob version to verify
@@ -166,18 +173,34 @@ library EigenDACertVerificationLib {
         }
         DATypesV1.VersionedBlobParams memory blobParams = eigenDAThresholdRegistry.getBlobParams(blobVersion);
 
-        // In order to prevent divide by 0 panic, we need gamma > 0 and codingRate > 0.
-        // We assume here that the CertVerifier constructor checked that confirmationThreshold > adversaryThreshold.
-        // We also checked above that the blobParams are from a valid version.
-        // Thus, dividing by codingRate below will only panic if codingRate of a proper initialized version is 0,
-        // which is either a configuration bug, or a malicious attack. In both cases, we cannot tell whether the
-        // cert is valid or invalid, so it is ok to panic and let social consensus intervene (put a human debugger in the loop).
-        uint256 gamma = securityThresholds.confirmationThreshold - securityThresholds.adversaryThreshold;
-        uint256 n = (10000 - ((1_000_000 / gamma) / uint256(blobParams.codingRate))) * uint256(blobParams.numChunks);
-        uint256 minRequired = blobParams.maxNumOperators * 10000;
-
-        if (!(n >= minRequired)) {
-            revert SecurityAssumptionsNotMet(gamma, n, minRequired);
+        // Check for potential underflow:
+        // maxNumOperators must not exceed numChunks
+        //
+        if (
+            blobParams.maxNumOperators > blobParams.numChunks
+                || securityThresholds.confirmationThreshold < securityThresholds.adversaryThreshold
+        ) {
+            revert SecurityAssumptionsNotMet(
+                securityThresholds.confirmationThreshold,
+                securityThresholds.adversaryThreshold,
+                blobParams.codingRate,
+                blobParams.numChunks,
+                blobParams.maxNumOperators
+            );
+        }
+
+        uint256 lhs = blobParams.codingRate * (blobParams.numChunks - blobParams.maxNumOperators)
+            * (securityThresholds.confirmationThreshold - securityThresholds.adversaryThreshold);
+        uint256 rhs = 100 * blobParams.numChunks;
+
+        if (!(lhs >= rhs)) {
+            revert SecurityAssumptionsNotMet(
+                securityThresholds.confirmationThreshold,
+                securityThresholds.adversaryThreshold,
+                blobParams.codingRate,
+                blobParams.numChunks,
+                blobParams.maxNumOperators
+            );
         }
     }
 
```

### contracts/test/unit/EigenDACertVerifierV2Unit.t.sol
```diff
@@ -7,6 +7,18 @@ import {EigenDATypesV2} from "src/core/libraries/v2/EigenDATypesV2.sol";
 import {EigenDATypesV1} from "src/core/libraries/v1/EigenDATypesV1.sol";
 import {EigenDACertTypes} from "src/integrations/cert/EigenDACertTypes.sol";
 import {EigenDACertVerifier} from "src/integrations/cert/EigenDACertVerifier.sol";
+import {IEigenDAThresholdRegistry} from "src/core/interfaces/IEigenDAThresholdRegistry.sol";
+
+// Test harness to expose internal library functions
+contract CertLibTestHarness {
+    function checkSecurityParams(
+        IEigenDAThresholdRegistry eigenDAThresholdRegistry,
+        uint16 blobVersion,
+        EigenDATypesV1.SecurityThresholds memory securityThresholds
+    ) external view {
+        CertLib.checkSecurityParams(eigenDAThresholdRegistry, blobVersion, securityThresholds);
+    }
+}
 
 contract EigenDACertVerifierV2Unit is MockEigenDADeployer {
     using stdStorage for StdStorage;
@@ -15,9 +27,12 @@ contract EigenDACertVerifierV2Unit is MockEigenDADeployer {
     address relay0 = address(uint160(uint256(keccak256(abi.encodePacked("relay0")))));
     address relay1 = address(uint160(uint256(keccak256(abi.encodePacked("relay1")))));
 
+    CertLibTestHarness certLibHarness;
+
     function setUp() public virtual {
         quorumNumbersRequired = hex"00";
         _deployDA();
+        certLibHarness = new CertLibTestHarness();
     }
 
     function _getDACert(uint256 seed) internal returns (EigenDACertTypes.EigenDACertV3 memory) {
@@ -49,6 +64,104 @@ contract EigenDACertVerifierV2Unit is MockEigenDADeployer {
         assertEq(res, uint8(EigenDACertVerifier.StatusCode.INVALID_CERT));
     }
 
+    function test_checkSecurityParams_ValidParams() public view {
+        // Uses the default blob params from MockEigenDADeployer:
+        // maxNumOperators: 3537, numChunks: 8192, codingRate: 8
+        // and default security thresholds: confirmationThreshold: 55, adversaryThreshold: 33
+
+        uint16 blobVersion = 0;
+        EigenDATypesV1.SecurityThresholds memory securityThresholds =
+            EigenDATypesV1.SecurityThresholds({confirmationThreshold: 55, adversaryThreshold: 33});
+
+        // This should not revert
+        certLibHarness.checkSecurityParams(eigenDAThresholdRegistry, blobVersion, securityThresholds);
+    }
+
+    function test_checkSecurityParams_revert_MaxNumOperatorsExceedsNumChunks() public {
+        // Create blob params where maxNumOperators > numChunks (underflow condition)
+        EigenDATypesV1.VersionedBlobParams memory invalidBlobParams = EigenDATypesV1.VersionedBlobParams({
+            maxNumOperators: 100,
+            numChunks: 50, // maxNumOperators > numChunks
+            codingRate: 8
+        });
+
+        // Add this as blob version 1
+        vm.prank(registryCoordinatorOwner);
+        eigenDAThresholdRegistry.addVersionedBlobParams(invalidBlobParams);
+
+        uint16 blobVersion = 1;
+        EigenDATypesV1.SecurityThresholds memory securityThresholds =
+            EigenDATypesV1.SecurityThresholds({confirmationThreshold: 55, adversaryThreshold: 33});
+
+        vm.expectRevert(
+            abi.encodeWithSelector(
+                CertLib.SecurityAssumptionsNotMet.selector,
+                securityThresholds.confirmationThreshold,
+                securityThresholds.adversaryThreshold,
+                invalidBlobParams.codingRate,
+                invalidBlobParams.numChunks,
+                invalidBlobParams.maxNumOperators
+            )
+        );
+        certLibHarness.checkSecurityParams(eigenDAThresholdRegistry, blobVersion, securityThresholds);
+    }
+
+    function test_checkSecurityParams_revert_ConfirmationLessThanAdversary() public {
+        uint16 blobVersion = 0;
+        // Create security thresholds where confirmationThreshold < adversaryThreshold (underflow condition)
+        EigenDATypesV1.SecurityThresholds memory invalidSecurityThresholds = EigenDATypesV1.SecurityThresholds({
+            confirmationThreshold: 30,
+            adversaryThreshold: 50 // confirmationThreshold < adversaryThreshold
+        });
+
+        EigenDATypesV1.VersionedBlobParams memory blobParams = eigenDAThresholdRegistry.getBlobParams(blobVersion);
+
+        vm.expectRevert(
+            abi.encodeWithSelector(
+                CertLib.SecurityAssumptionsNotMet.selector,
+                invalidSecurityThresholds.confirmationThreshold,
+                invalidSecurityThresholds.adversaryThreshold,
+                blobParams.codingRate,
+                blobParams.numChunks,
+                blobParams.maxNumOperators
+            )
+        );
+        certLibHarness.checkSecurityParams(eigenDAThresholdRegistry, blobVersion, invalidSecurityThresholds);
+    }
+
+    function test_checkSecurityParams_revert_SecurityInequalityFails() public {
+        // Create parameters that fail the security inequality:
+        // codingRate * (numChunks - maxNumOperators) * (confirmationThreshold - adversaryThreshold) >= 100 * numChunks
+
+        // Create blob params with tight constraints
+        EigenDATypesV1.VersionedBlobParams memory tightBlobParams =
+            EigenDATypesV1.VersionedBlobParams({maxNumOperators: 3, numChunks: 16, codingRate: 2});
+
+        vm.prank(registryCoordinatorOwner);
+        eigenDAThresholdRegistry.addVersionedBlobParams(tightBlobParams);
+
+        uint16 blobVersion = 1;
+
+        // Use thresholds that will fail the inequality
+        // LHS = 2 * (16 - 3) * (55 - 33) = 572
+        // RHS = 100 * 16 = 1600
+        // 572 < 1600, so this should fail
+        EigenDATypesV1.SecurityThresholds memory insecureThresholds =
+            EigenDATypesV1.SecurityThresholds({confirmationThreshold: 55, adversaryThreshold: 33});
+
+        vm.expectRevert(
+            abi.encodeWithSelector(
+                CertLib.SecurityAssumptionsNotMet.selector,
+                insecureThresholds.confirmationThreshold,
+                insecureThresholds.adversaryThreshold,
+                tightBlobParams.codingRate,
+                tightBlobParams.numChunks,
+                tightBlobParams.maxNumOperators
+            )
+        );
+        certLibHarness.checkSecurityParams(eigenDAThresholdRegistry, blobVersion, insecureThresholds);
+    }
+
     function _getSignedBatchAndBlobVerificationProof(uint256 pseudoRandomNumber, uint8 version)
         internal
         returns (
```

### docs/spec/src/protocol/architecture/security-parameters.md
```diff
@@ -42,7 +42,7 @@ In this section, we prove that, with our [chunk assignment algorithm](./assignme
 $$
 r = \frac{c}{c-n} \gamma 
 $$
-
+, where $c > n$.
 In other words, we want to prove that any subset of validators with $\frac{c}{c-n} \gamma$ of total stake collectively own enough chunks to reconstruct the original blob. 
 Formally, we need to show that for any set of validators $H$ with total stake $\sum_{i \in H} \eta_i \geq \frac{c}{c-n} \gamma$, the chunks assigned to $H$ satisfy $\sum_{i \in H} c_i \geq \gamma c$. 
 
@@ -138,41 +138,50 @@ A table of the security thresholds is given below for the reader's reference, as
 In our code, we use slightly different names for the security thresholds compared to the notation in this document.  
 Here is the mapping from the notations in this doc to the variable names in the code:  
 
-- `ConfirmationThreshold` → `securityThresholds.confirmationThreshold`  
-- `SafetyThreshold` → `securityThresholds.adversaryThreshold`
+- `ConfirmationThreshold` → `securityThresholds.confirmationThreshold` (in percent)
+- `SafetyThreshold` → `securityThresholds.adversaryThreshold` (in percent)
 - $c$ → `blobParams.numChunks`
 - $n$ → `blobParams.maxNumOperators`
 - $\gamma$ → 1 / `blobParams.codingRate`
 
 Note that `SafetyThreshold` is called `adversaryThreshold` in the code.
 
+Also, `securityThresholds.confirmationThreshold` and `securityThresholds.adversaryThreshold` are expressed in percent where the stored integer equals the required percentage. 
+For example, `securityThresholds.confirmationThreshold = 55` means `ConfirmationThreshold = 55%`.
+
 **1. Safety Threshold**
 
-The check for the inequality (1) above is implemented as follows ([see in code](https://github.com/Layr-Labs/eigenda/blob/6cd192ecbe5f0abfe73fc08df306cf00e32ef010/contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol#L188)).
+The check for the inequality (1) above is implemented as follows ([see in code](https://github.com/Layr-Labs/eigenda/blob/b06b0bf50917bb6aa1967d1dc12d5b7de815562f/contracts/src/integrations/cert/libraries/EigenDACertVerificationLib.sol#L163)).
 
 ```solidity
-function checkSecurityParams(
-    DATypesV1.VersionedBlobParams memory blobParams,
-    DATypesV1.SecurityThresholds memory securityThresholds
-) internal pure returns (StatusCode err, bytes memory errParams) {
-    uint256 gamma = securityThresholds.confirmationThreshold - securityThresholds.adversaryThreshold;
-    uint256 n = (10000 - ((1_000_000 / gamma) / uint256(blobParams.codingRate))) * uint256(blobParams.numChunks);
-    uint256 minRequired = blobParams.maxNumOperators * 10000;
-
-    if (n >= minRequired) {
-        return (StatusCode.SUCCESS, "");
-    } else {
-        return (StatusCode.SECURITY_ASSUMPTIONS_NOT_MET, abi.encode(gamma, n, minRequired));
-    }
+// Check for potential underflow: maxNumOperators must not exceed numChunks
+if (blobParams.maxNumOperators > blobParams.numChunks) {
+    revert SecurityAssumptionsNotMet(
+        ...
+    );
+}
+
+uint256 lhs = blobParams.codingRate * (blobParams.numChunks - blobParams.maxNumOperators) * (securityThresholds.confirmationThreshold - securityThresholds.adversaryThreshold);
+uint256 rhs = 100 * blobParams.numChunks;
+
+if (!(lhs >= rhs)) {
+    revert SecurityAssumptionsNotMet(
+        ...
+    );
 }
 ```
-Specifically, the code above implements a check for the following inequality:  
+First, the code confirms that the total number of chunks is greater than the total number of validators $(c > n)$ so that `ReconstructionThreshold` is meaningful. Next, it validates the following inequality:  
+
+`blobParams.codingRate * (blobParams.numChunks - blobParams.maxNumOperators) * (securityThresholds.confirmationThreshold - securityThresholds.adversaryThreshold) >= 100 * blobParams.numChunks`
 
-`(10000 - ((1_000_000 / (securityThresholds.confirmationThreshold - securityThresholds.adversaryThreshold)) / uint256(blobParams.codingRate))) * uint256(blobParams.numChunks) >= blobParams.maxNumOperators * 10000`  
+The inequality above can be be rewritten as:
+`(blobParams.numChunks - blobParams.maxNumOperators) / 100 >= blobParams.numChunks / (blobParams.codingRate * (blobParams.numChunks - blobParams.maxNumOperators))`
 
 By substituting the variables using the notation mapping shown at the beginning of this section and simplifying, we get:  
-`ConfirmationThreshold - SafetyThreshold >= (c / (c - n)) * γ = ReconstructionThreshold`, 
-which is exactly inequality (1) shown in the previous subsection.  
+`(ConfirmationThreshold - SafetyThreshold) >= (c / (c - n)) * γ`.
+
+Recall that `ReconstructionThreshold = (c / (c - n)) * γ, (c > n)`(see more details in [Reconstruction Threshold](#reconstruction-threshold)).
+Therefore, the inequality above is exactly inequality (1) shown in the previous subsection.  
 
 **2. Liveness Threshold**
 
```
