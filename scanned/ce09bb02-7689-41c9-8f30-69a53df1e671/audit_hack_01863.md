# [C] Directly Exposed Private Key Export

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The snap can access the BIP44 entropy for Filecoin's private keys, granting it considerable power over MetaMask's private keys. Specifically, the `fil_exportPrivateKey` command lets dapps obtain the private key programmatically, pending user consent. However, there's a heightened risk of users indiscriminately granting this permission. To maintain MetaMask's security integrity, the snap should mirror the same rigorous security standards to mitigate the effect of phishing attacks and malicious dapps.


**packages/snap/src/rpc/export-private-key.ts:L19-L34**
```solidity
export async function exportPrivateKey(
  ctx: SnapContext
): Promise<ExportPrivateKeyResponse> {
  const conf = await snapDialog(ctx.snap, {
    type: 'confirmation',
    content: panel([heading(`Do you want to export your private key?`)]),
  })

  if (conf) {
    return {
      result: base64pad.encode(ctx.account.privateKey),
      error: null,
    }
  }
  return serializeError('User denied private key export')
}
```

#### Recommendation

The development team should reconsider providing such a sensitive functionality. Instead of programmatically exposing the private key, use a dialog that prompts users to copy the private key manually. This approach, consistent with MetaMask's default, encourages users to deliberate their actions more thoroughly.
